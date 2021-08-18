import numpy as np

func_types =[
  "Publication_publish", # 0
  "Publisher_publish", # 1
  "Publication_enqueueMessage", # 2

  "SubscriptionQueue_push", # 3
  "SubscriptionQueue_call_before_callback", # 4
  "SubscriptionQueue_call_after_callback",

  "TransportTCP_write", # 6
  "TransportTCP_read", # 7

  "accept",
  "connect",
  "bind",

  "SubscriptionQueue_call_before_callback_2",
  ]

# 2 1613531009784539434 11345 11361 2 2
def collect(name):
    node = dict()
    node["Publication_publish"] = dict()
    node["Publisher_publish"] = dict()
    node["Publisher_publish"]["time"] = list()
    node["Publication_enqueueMessage"] = dict()
    node["SubscriptionQueue_push"] = dict()
    node["SubscriptionQueue_call_before_callback"] = dict()
    node["SubscriptionQueue_call_after_callback"] = dict()
    node["TransportTCP_write"] = dict()
    node["TransportTCP_read"] = dict()
    node["socket"] = dict()
    node["port"] = list()
    node["SubscriptionQueue_call_before_callback_2"] = dict()

    with open(name) as f:
        for _l in f.readlines():
            l = _l.split()

            try:
                f_type = func_types[int(l[0])]
            except:
                continue
            seq1 = int(l[4])
            seq2 = int(l[5])
            time = int(l[1])
            pid = int(l[2])
            tid = int(l[3])
            name = l[6]

            if f_type == "Publisher_publish":
                node["Publisher_publish"][seq2] = dict()
                node["Publisher_publish"][seq2]["time"] = time
                node["Publisher_publish"]["time"].append(time)

            elif f_type == "Publication_publish":
                node["Publication_publish"][seq2] = dict()
                node["Publication_publish"][seq2]["time"] = time

            elif f_type == "Publication_enqueueMessage":
                node["Publication_enqueueMessage"][seq1] = dict()
                node["Publication_enqueueMessage"][seq1]["time"] = time
                node["Publication_enqueueMessage"][seq1]["seq"] = seq2

            elif f_type == "SubscriptionQueue_push":
                node["SubscriptionQueue_push"][seq1] = dict()
                node["SubscriptionQueue_push"][seq1]["time"] = time
                node["SubscriptionQueue_push"][seq1]["seq"] = seq2

            elif f_type == "SubscriptionQueue_call_before_callback":
                node["SubscriptionQueue_call_before_callback"][seq1] = dict()
                node["SubscriptionQueue_call_before_callback"][seq1]["time"] = time
                node["SubscriptionQueue_call_before_callback"][seq1]["seq"] = seq2
                node["SubscriptionQueue_call_before_callback"][seq1]["name"] = name

            elif f_type == "SubscriptionQueue_call_after_callback":
                node["SubscriptionQueue_call_after_callback"][seq1] = dict()
                node["SubscriptionQueue_call_after_callback"][seq1]["time"] = time

            elif f_type == "TransportTCP_write":
                node["TransportTCP_write"][seq1] = dict()
                node["TransportTCP_write"][seq1]["time"] = time

            elif f_type == "TransportTCP_read":
                sock = seq1
                seq = seq2
                if not seq in node["TransportTCP_read"].keys():
                    node["TransportTCP_read"][seq] = dict()
                node["TransportTCP_read"][seq][sock] = dict()
                node["TransportTCP_read"][seq][sock]["time"] = time

            elif f_type == "accept":
                if not seq2 in node["socket"].keys():
                    node["socket"][seq2] = dict()
                node["socket"][seq2]["to"] = seq1

            elif f_type == "connect":
                if not seq2 in node["socket"].keys():
                    node["socket"][seq2] = dict()
                node["socket"][seq2]["to"] = seq1

            elif f_type == "bind":
                if not seq2 in node["socket"].keys():
                    node["socket"][seq2] = dict()
                node["socket"][seq2]["from"] = seq1
                node["port"].append(seq1)

            elif f_type == "SubscriptionQueue_call_before_callback_2":
                node["SubscriptionQueue_call_before_callback_2"][seq1] = dict()
                node["SubscriptionQueue_call_before_callback_2"][seq1]["time"] = time
            else:
                print("Error")
    return node

def collect_nw(name):
    tl = list()
    send = list()
    recv = list()
    with open(name) as f:
        lines = f.readlines()
        for i in range(len(lines)//4):
            s = lines[4*i].split()
            s2 = lines[4*i+1].split()
            s3 = lines[4*i+2].split()
            s4 = lines[4*i+3].split()
            tl.append(int(s[0])*1000)
            send.append(int(s[1])+int(s2[1])+int(s3[1])+int(s4[1]))
            recv.append(int(s[2])+int(s2[2])+int(s3[2])+int(s4[2]))

    return tl,send,recv

def calc_cb(node_name,option):
    node = collect(node_name)
    lat = dict()

    for seq1, t in node["SubscriptionQueue_call_before_callback"].items():
        time1 = t["time"]
        seq2 = t["seq"]
        name = t["name"]

        try:
            time2 = node["SubscriptionQueue_call_after_callback"][seq1]["time"]
        except:
            continue

        if not name in lat.keys():
            lat[name] = dict()
            lat[name]["Callback"] = list()

        lat[name]["Callback"].append(time2 - time1)
    return lat

def calc_lat_intra(node,option):
    node = collect(node_name)
    lat = dict()

    for seq, t in node["SubscriptionQueue_push"].items():
        time1 = t["time"]
        seq_p = t["seq"]

        try:
            time2 = node["SubscriptionQueue_call_before_callback"][seq_p]["time"]
            name  = node["SubscriptionQueue_call_before_callback"][seq_p]["name"]
        except:
            continue

        if seq in node["TransportTCP_read"].keys():
            continue

        if not name in lat.keys():
            lat[name] = dict()
            lat[name]["SubQ"] = list()

        lat[name]["SubQ"].append(time2 - time1)
    return lat

def calc_lat_inter(node1_name, node2_name, option):
    node1 = collect(node1_name)
    node2 = collect(node2_name)

    lat = dict()
    timeline = dict()

    for seq, t in node1["Publication_publish"].items():
        if seq == 0:
            print("seq",seq)
            continue
        time1 = t["time"]

        try:
            time0 = 0
            for tt in node1["Publisher_publish"]["time"]:
                if tt > time1:
                    break
                time0 = tt
        except:
            print("time0 - time1", seq)
            continue
        if time0 > time1:
            print("Error: time0 > time1 at ", seq)
            continue
        try:
            time2 = node1["Publication_enqueueMessage"][seq]["time"]
            seq_e = node1["Publication_enqueueMessage"][seq]["seq"]

            time3 = node1["TransportTCP_write"][seq_e]["time"]
        except:
            print("time2 - time3", seq)
            continue
        if time1 > time2:
            print("Error: time1 at ", seq, " > time2 at ", seq_e)
            continue

        try:
            node2["TransportTCP_read"][seq_e]
        except:
            print("TransportTCP_read", seq_e)
            continue

        time4 = 0
        for sock, t in node2["TransportTCP_read"][seq_e].items():
            try:
                if node2["socket"][sock]["to"] in node1["port"]:
                    time4 = t["time"]
                    pass
            except:
                print("Error: time4 at ", seq_e)
                continue
        if time4 - time3 < 0:
            continue

        try:
            time5 = node2["SubscriptionQueue_push"][seq_e]["time"]
            seq_p = node2["SubscriptionQueue_push"][seq_e]["seq"]


            time7 = node2["SubscriptionQueue_call_before_callback"][seq_p]["time"]
            seq_c = node2["SubscriptionQueue_call_before_callback"][seq_p]["seq"]
            name = node2["SubscriptionQueue_call_before_callback"][seq_p]["name"]

            time6 = node2["SubscriptionQueue_call_before_callback_2"][seq_p]["time"]

        except Exception as e:
            print("time5 - tim6", e)
            continue

        if not name in lat.keys():
            lat[name] = dict()
            lat[name]["PubQ"] = list()
            lat[name]["Kernel"] = list()
            lat[name]["SubQ"] = list()

            timeline[name] = dict()
            timeline[name]["PubQ"] = list()
            timeline[name]["Kernel"] = list()
            timeline[name]["SubQ"] = list()

            if not hasattr(option,"ros_detail") or not option.ros_detail:
                lat[name]["ROS"] = list()
                timeline[name]["ROS"] = list()
            else:
                lat[name]["ROS: App - PubQ"] = list()
                lat[name]["ROS: PubQ - send"] = list()
                lat[name]["ROS: recv - SubQ"] = list()
                lat[name]["ROS: SubQ - App"] = list()

                timeline[name]["ROS: App - PubQ"] = list()
                timeline[name]["ROS: PubQ - send"] = list()
                timeline[name]["ROS: recv - SubQ"] = list()
                timeline[name]["ROS: SubQ - App"] = list()

        lat[name]["PubQ"].append(time2 - time1)
        lat[name]["Kernel"].append(time4 - time3)
        lat[name]["SubQ"].append(time6 - time5)

        timeline[name]["PubQ"].append(time1)
        timeline[name]["Kernel"].append(time3)
        timeline[name]["SubQ"].append(time5)

        if not hasattr(option,"ros_detail") or not option.ros_detail:
            lat[name]["ROS"].append(time7 - time0 - (time6 - time5) - (time4 - time3) - (time2 - time1))
        else:
            lat[name]["ROS: App - PubQ"].append(time1 - time0)
            lat[name]["ROS: PubQ - send"].append(time3 - time2)
            lat[name]["ROS: recv - SubQ"].append(time5 - time4)
            lat[name]["ROS: SubQ - App"].append(time7 - time6)

            timeline[name]["ROS: App - PubQ"].append(time0)
            timeline[name]["ROS: PubQ - send"].append(time2)
            timeline[name]["ROS: recv - SubQ"].append(time4)
            timeline[name]["ROS: SubQ - App"].append(time4)

    return lat,timeline

def calc_cdf(thread_name, option):
    with open(thread_name) as f:
        l =f.readlines()
    return np.array(list(map(lambda x: int(x.split()[1]), l)))

def calc_cpu(thread_name, option):
    time = list()
    cpu = list()
    with open(thread_name,'r') as f:
        for l in f.readlines():
            cpu.append(int(l.split()[1]))
            time.append(int(l.split()[2]))
    offset = time[0]
    tl = [(t - offset) for t in time ]
    return np.array(tl),np.array(cpu)
