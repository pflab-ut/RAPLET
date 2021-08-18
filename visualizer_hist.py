import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from functools import reduce
import sys
import subprocess
from statistics import mean, variance, stdev, median_grouped
from matplotlib.ticker import FormatStrFormatter

from visualizer_calc import *

def show_inter(args):
    lat,timeline = calc_lat_inter(args.src_node, args.dst_node, args)

    node_num = len(lat)
    if node_num == 0:
        print("None")
        sys.exit(0)

    time_num = len(list(lat.values())[0])

    if args.concat:
        fig, ax = plt.subplots(node_num, time_num, sharex="row", sharey="row",squeeze=False)
    else:
        fig, ax = plt.subplots(node_num, 1, sharex="row", sharey="row",squeeze=False)

    for i,(node_name, node_time) in enumerate(lat.items(), start=0):
        assert reduce(lambda x,y: x if len(x) == len(y) else False, node_time.values())
        try:
            demangler_out = subprocess.run(["./demangler", node_name], capture_output=True)
            node_name = demangler_out.stdout.decode('utf-8')
        except:
            print("error: demangler")

        print()
        print(node_name)
        print("num: ", len(list(node_time.values())[0]))

        ax[i,0].set_ylabel("# messages")
        for j,(lat_name, time_)  in enumerate(node_time.items()):
            time = [ t / float(1e6) for t in time_]
            if args.concat:
                print(max(time), time.index(max(time)))
                ax[i,j].xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
                ax[i,j].grid()
                ax[i,j].set_axisbelow(True)
                ax[i,j].hist(time, bins =100, histtype = 'bar', color="gray")
                ax[i,j].set_title(lat_name)
                ax[i,j].set_xlabel("Latency (ms)", fontsize=26)
                ax[i,j].tick_params(axis = 'x',pad=10)
            else:
                print(max(time), time.index(max(time)))
                ax[i,0].grid()
                ax[i,0].hist(time, bins =100, histtype = 'step', label = lat_name)
                ax[i,0].legend(loc="best")

    plt.xlim(0,0.1)
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()

def show_intra(args):
    lat = calc_lat_intra(args.node,args)

    fig = plt.figure()

    node_num = len(lat)

    if node_num == 0:
        print("None")
        sys.exit(0)

    for i,(node_name, node_time) in enumerate(lat.items(), start=0):
        assert reduce(lambda x,y: x if len(x) == len(y) else False, node_time.values())
        try:
            demangler_out = subprocess.run(["./demangler", node_name], capture_output=True)
            node_name = demangler_out.stdout.decode('utf-8')
        except:
            print("error: demangler")

        print()
        print(node_name)
        print("num: ", len(list(node_time.values())[0]))

        time_num = len(node_time)
        for j,(lat_name, time)  in enumerate(node_time.items(), start=1):
            if args.concat:
                ax = fig.add_subplot(node_num, time_num, time_num*i+j)
            else:
                ax = fig.add_subplot(node_num,1,1)
            ax.hist(time, bins =50, histtype = 'bar', label = lat_name)
            ax.legend(loc="best")

    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
