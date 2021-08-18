import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from functools import reduce
import sys  
import subprocess
import argparse
import pandas as pd
from statistics import mean, variance, stdev, median_grouped

def show_timeline(args):
    n1 = collect(args.src_node)
    n2 = collect(args.dst_node)

    if args.pickup == None:
        print("Please select: Kernel, pubq, subq, ros")
        sys.exit(0)
    pickup_num = len(args.pickup)

    lat, timeline = calc_e2e_inter(n1,n2, args)

    node_num = len(lat)
    if node_num == 0:
        print("None")
        sys.exit(0)

    time_num = len(list(lat.values())[0])

    fig, ax = plt.subplots(node_num, pickup_num, sharex="row", sharey="row",squeeze=False)

    if args.nw != "":
        tl,send,recv = collect_nw(args.nw)

    for i,(node_name, node_time) in enumerate(lat.items(), start=0):
        assert reduce(lambda x,y: x if len(x) == len(y) else False, node_time.values())
        try:
            demangler_out = subprocess.run(["./demangler", node_name], capture_output=True)
            node_name_demangle = demangler_out.stdout.decode('utf-8')
        except:
            print("error: demangler")
            node_name_demangle = ""

        sample_num = len(list(node_time.values())[0])
        print()
        print(node_name, " (", node_name_demangle, ")")
        print("num: ", sample_num)

        tl2 = []
        if args.nw != "":
            for t in tl:
                tl2.append((t - min(tl))/(max(tl) - min(tl))*sample_num)

        for j,key in enumerate(args.pickup):
            print(key,min(lat[node_name][key]))
            ax[i,j].plot(range(len(timeline[node_name][key])), lat[node_name][key])
            ax[i,j].set_title(key)
            ax[i,j].set_xlabel("# messages")
            if j == 0:
                ax[i,j].set_ylabel("Latency (ns)")
            ax[i,j].zorder = 2
            ax[i,j].patch.set_visible(False)
            if args.nw != "":
                ax2 = ax[i,j].twinx()
                ax2.zorder = 1
                ax2.plot(tl2,send,color="orange")
                #ax2.plot(tl,recv,color="black")
                if j == len(args.pickup) - 1:
                    ax2.set_ylabel("Bandwidth (a.u.)")
    plt.show()


