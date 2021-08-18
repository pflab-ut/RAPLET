bpf_text_get_tid = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <linux/nsproxy.h>
#include <linux/pid_namespace.h>
#include <net/sock.h>
#include <bcc/proto.h>


struct data_t {
    // char type[16];
    u32 type;
    u32 tgid;
    u32 pid;
};
BPF_PERF_OUTPUT(data_pid);

struct data_init {
    u32 tgid;
};
BPF_PERF_OUTPUT(data_init);

struct delta {
    u32 pid;
    u32 tgid;
    u64 ns;
};

BPF_PERF_OUTPUT(data_delta);

// const char* iothread = "iothread";
#define IOTHREAD 0
#define PUBLISH 1

BPF_HASH(ros_pids, u32, u32);

BPF_HASH(start, u32);

BPF_HASH(bytes, u64, u64);

////////////

int init(struct pt_regs *ctx) {
    struct data_init data = {};

    u64 id = bpf_get_current_pid_tgid();
    data.tgid = id >> 32;

    u32 k = 0;
    ros_pids.update(&data.tgid, &k);

    data_init.perf_submit(ctx, &data, sizeof(data));
    return 0;
}

/*
int enqueueMessage(struct pt_regs *ctx) {
    struct data_t data = {};

    u64 id = bpf_get_current_pid_tgid();
    data.tgid = id >> 32;
    data.pid = id;
    data.type = IOTHREAD;

    u64 *is_ros_app,k = 0;
    is_ros_app = ros_pids.lookup(&data.pid); 
    if (is_ros_app == NULL) { 
        ros_pids.update(&data.pid, &k);
    }

    data_pid.perf_submit(ctx, &data, sizeof(data));
    return 0;
}

int publish(struct pt_regs *ctx) {
    struct data_t data = {};

    u64 id = bpf_get_current_pid_tgid();
    data.tgid = id >> 32;
    data.pid = id;
    data.type = PUBLISH;

    u64 *is_ros_app,k = 0;
    is_ros_app = ros_pids.lookup(&data.pid); 
    if (is_ros_app == NULL) { 
        ros_pids.update(&data.pid, &k);
    }

    data_pid.perf_submit(ctx, &data, sizeof(data));
    return 0;
}
*/

static int trace_enqueue(u32 tgid, u32 pid)
{

    u32 *is_ros_app = ros_pids.lookup(&tgid);
    if (is_ros_app == NULL) 
        return 0;

    u64 ts = bpf_ktime_get_ns();
    start.update(&pid, &ts);
    return 0;
}

int trace_wake_up_new_task(struct pt_regs *ctx, struct task_struct *p)
{
    return trace_enqueue(p->tgid, p->pid);
}

int trace_ttwu_do_wakeup(struct pt_regs *ctx, struct rq *rq, struct task_struct *p,
    int wake_flags)
{
    return trace_enqueue(p->tgid, p->pid);
}

// calculate latency
int trace_run(struct pt_regs *ctx, struct task_struct *prev)
{
    u32 tgid,pid;
    // ivcsw: treat like an enqueue event and store timestamp
    // memo: ivcsw はpreemptされてすぐにQに入る
    if (prev->state == TASK_RUNNING) {
        tgid = prev->tgid;

        u32 *is_ros_app = ros_pids.lookup(&tgid);
        if (is_ros_app != NULL) {
            u64 ts = bpf_ktime_get_ns();
            start.update(&tgid, &ts);
        }
    }

    tgid = bpf_get_current_pid_tgid() >> 32;
    pid = bpf_get_current_pid_tgid();

    u32 *is_ros_app = ros_pids.lookup(&tgid);
    if (is_ros_app == NULL) 
        return 0;

    u64 *tsp;
    struct delta data = {};

    // fetch timestamp and calculate delta
    tsp = start.lookup(&pid);
    if (tsp == 0) {
        return 0;   // missed enqueue
    }

    data.pid = pid;
    data.tgid = tgid;
    data.ns = bpf_ktime_get_ns() - *tsp;

    data_delta.perf_submit(ctx, &data, sizeof(data));

    start.delete(&pid);
    return 0;

}


int trace_tcp_sendmsg(struct pt_regs *ctx, struct sock *sk,
    struct msghdr *msg, size_t size)
{
    u16 dport = 0, family = sk->__sk_common.skc_family;
    if (family == AF_INET) {
        u64 send = 0;
        bytes.increment(send, size);
    } else if (family == AF_INET6) {
        u64 send = 0;
        bytes.increment(send, size);
    }
    // else drop
    return 0;
}

int trace_tcp_cleanup_rbuf(struct pt_regs *ctx, struct sock *sk, int copied)
{
    if (copied <= 0)
        return 0;

    u16 dport = 0, family = sk->__sk_common.skc_family;
    if (family == AF_INET) {
        u64 recv = 1;
        bytes.increment(recv, copied);
    } else if (family == AF_INET6) {
        u64 recv = 1;
        bytes.increment(recv, copied);
    }
    // else drop
    return 0;
}
"""

