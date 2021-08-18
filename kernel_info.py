from __future__ import print_function
from bcc import BPF
from time import strftime, time
from ctypes import c_ulong


from ki_text import *
libroscpp_path = "/opt/ros/melodic/lib/libroscpp.so"

ros_app_tgid = list()
ros_app_pid_tgid = dict()
ros_app_pids_delta = dict()

bpf_get_tid = BPF(text=bpf_text_get_tid)

nw = dict()
nw["send"] = list()
nw["recv"] = list()

# def get_tid_attach(tgid):
#     # Publication::enqueueMessage(ros::SerializedMessage const&)
#     bpf_get_tid.attach_uprobe(name=libroscpp_path, pid = tgid,
#             sym="_ZN3ros11Publication14enqueueMessageERKNS_17SerializedMessageE", fn_name="enqueueMessage")
# 
#     # ros::SubscriptionQueue::call()
#     bpf_get_tid.attach_uprobe(name=libroscpp_path, pid = tgid,
#             sym="_ZN3ros17SubscriptionQueue4callEv", fn_name="publish")
# 
#     # ros::SubscriptionQueue::call()
#     bpf_get_tid.attach_uprobe(name=libroscpp_path, pid = tgid,
#             sym="_ZN3ros11Publication7publishERNS_17SerializedMessageE", fn_name="publish")

def get_tid_detach(tgid, func):
    if (func == "enqueueMessage"):
        try:
            # Publication::enqueueMessage(ros::SerializedMessage const&)
            bpf_get_tid.detach_uprobe(name=libroscpp_path, pid = tgid,
                    sym="_ZN3ros11Publication14enqueueMessageERKNS_17SerializedMessageE")
        except:
            print("detach IO error")

    if (func == "pubsub"):
        try:
            # ros::SubscriptionQueue::call()
            bpf_get_tid.detach_uprobe(name=libroscpp_path, pid = tgid,
                    sym="_ZN3ros17SubscriptionQueue4callEv")

            bpf_get_tid.detach_uprobe(name=libroscpp_path, pid = tgid,
                    sym="_ZN3ros11Publication7publishERNS_17SerializedMessageE")
        except:
            print("detach pubsub error")




def ros_init():
    bpf_get_tid.attach_uprobe(name=libroscpp_path,
            sym="_ZN3ros4initERiPPcRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEj", fn_name="init")

def sched_check():
    bpf_get_tid.attach_kprobe(event="ttwu_do_wakeup", fn_name="trace_ttwu_do_wakeup")
    bpf_get_tid.attach_kprobe(event="wake_up_new_task", fn_name="trace_wake_up_new_task")
    bpf_get_tid.attach_kprobe(event="finish_task_switch", fn_name="trace_run")

def nw_check():
    bpf_get_tid.attach_kprobe(event="tcp_sendmsg", fn_name="trace_tcp_sendmsg")
    bpf_get_tid.attach_kprobe(event="tcp_cleanup_rbuf", fn_name="trace_tcp_cleanup_rbuf")

def print_get_pid(cpu, data, size):
    event = bpf_get_tid["data_pid"].event(data)

    if event.type == 0:
        print('IOTHREAD detected:  PID- %d, TID- %d '%(event.tgid, event.pid))
        get_tid_detach(event.tgid, "enqueueMessage")
        ros_app_pids[event.pid] = "IOTHREAD" 
        ros_app_pids_delta[event.pid] = [] 

    elif event.type == 1:
        print('CALLBACKTHREAD detected:  PID- %d, TID- %d '%(event.tgid, event.pid))
        get_tid_detach(event.tgid, "pubsub")
        ros_app_pids[event.pid] = "CALLBACKTHREAD" 
        ros_app_pids_delta[event.pid] = []


def print_init(cpu, data, size):
    event = bpf_get_tid["data_init"].event(data)
    tgid = event.tgid
    ros_app_tgid.append(tgid)
    # get_tid_attach(tgid)

def print_delta(cpu, data, size):
    event = bpf_get_tid["data_delta"].event(data)
    if not event.pid in ros_app_pids_delta.keys():
        ros_app_pids_delta[event.pid] = list()
        ros_app_pid_tgid[event.pid] = event.tgid
    ros_app_pids_delta[event.pid].append(event.ns)


bpf_get_tid["data_pid"].open_perf_buffer(print_get_pid)
bpf_get_tid["data_init"].open_perf_buffer(print_init)
bpf_get_tid["data_delta"].open_perf_buffer(print_delta)

ros_init()
sched_check()
nw_check()

while 1:
    try:
        bpf_get_tid.perf_buffer_poll(timeout=100)

        t = int(time()*1000000)
        k = map(lambda x: x.value, bpf_get_tid["bytes"].keys())

        if 0 in k:
            nw["send"].append((t, int(bpf_get_tid["bytes"][c_ulong(0)].value)))
        else:
            nw["send"].append((t, 0))

        if 1 in k:
            nw["recv"].append((t, int(bpf_get_tid["bytes"][c_ulong(1)].value)))
        else:
            nw["recv"].append((t, 0))

        bpf_get_tid["bytes"].clear()

    except KeyboardInterrupt:
        for pid, vals in ros_app_pids_delta.items():
            with open("data/qlat" +str(ros_app_pid_tgid[pid]) + "-" + str(pid) + ".txt", "w") as f:
                f.write("\n".join(map(lambda x: "Q " + str(x), vals)))
        tgids = str(min(ros_app_tgid)) + "-" + str(max(ros_app_tgid))
        with open("data/nw"+tgids,"w") as f:
            for i in range(len(nw["send"])):
                t,ps = nw["send"][i]
                t,pr = nw["recv"][i]
                f.write(str(t) + " " + str(ps) + " " + str(pr)+ "\n")
        exit()
