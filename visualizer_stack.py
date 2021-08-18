import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from functools import reduce
import sys
import subprocess
import argparse
from statistics import mean, variance, stdev, median_grouped

from visualizer_calc import *

plt.rcParams['figure.subplot.top'] = 0.9
plt.rcParams['figure.subplot.bottom'] = 0.155
plt.rcParams['figure.subplot.left'] = 0.080
plt.rcParams['figure.subplot.right'] = 0.995

def show_stack(args):
    latencies_mean = list()
    latencies_99 = list()
    lat_source = list()
    index = list()

    node_num = len(args.nodes)
    for nodes in args.nodes:
        lat,timeline = calc_lat_inter(nodes[0],nodes[1],args)

        index.append(nodes[2].replace(r"\n", "\n"))

        topic_num = len(lat)
        if topic_num != 1:
            print("Error: the number of topic must be 1. ",nodes[2])
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

            lat_mean = list()
            lat_99 = list()
            lat_source = list()
            for j,(lat_name, time)  in enumerate(node_time.items(), start=1):
                    print(mean(time)/float(1e6))
                    lat_mean.append(mean(time)/float(1e6))
                    lat_99.append(np.percentile(time,99)/float(1e6))
                    lat_source.append(lat_name)

            latencies_mean.append(lat_mean)
            latencies_99.append(lat_99)

    fig, ax = plt.subplots()

    t_lat_mean = list(zip(*latencies_mean))
    t_lat_99 = list(zip(*latencies_99))
    x = np.arange(node_num)
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

    width = 0.3
    if args.nnpercentile:
        bot = np.array( [0] * node_num)
        for i,source_name in enumerate(lat_source):
            bar1 = ax.bar(x - width/2, t_lat_mean[i], width-0.03, bottom = bot, alpha = 0.9,  label=source_name, edgecolor='black')
            bot = bot + np.array(t_lat_mean[i])

        bot = np.array( [0] * node_num)
        for i,source_name in enumerate(lat_source):
            bar2 = ax.bar(x + width/2, t_lat_99[i], width-0.03, bottom = bot, color=colors[i], alpha = 0.9,  edgecolor='black')
            bot = bot + np.array(t_lat_99[i])

        sublabel_y_pos = -0.005
        for rect in bar1:
            ax.text(rect.get_x() + rect.get_width()/2.0, sublabel_y_pos, "mean ", fontsize=20, ha="center", va="top")

        for rect in bar2:
            ax.text(rect.get_x() + rect.get_width()/2.0, sublabel_y_pos, "99th", fontsize=20, ha="center", va="top")

        ax.set_xticks(x)
        ax.set_xticklabels(index, fontsize=24)
        ax.tick_params(axis = 'x',pad=25)

        for i  in range(len(latencies_mean)):
            print(sum(latencies_99[i])/sum(latencies_mean[i]))

    else:
        bot = np.array( [0] * node_num)
        for i,source_name in enumerate(lat_source):
            ax.bar(x, t_lat_mean[i], width-0.03, bottom = bot, alpha = 0.9, label=source_name, edgecolor='black')
            bot = bot + np.array(t_lat_mean[i])
        ax.set_xticks(x)
        ax.set_xticklabels(index, fontsize=23)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(reversed(handles), reversed(labels), loc="upper right",fontsize=22)
    plt.xticks(rotation=0)
    plt.grid(axis='y')
    ax.set_axisbelow(True)
    plt.ylim(0,0.7)

    plt.ylabel("Latency (ms)")

    plt.show()

def show_stack_comp_cb(args):
    latencies_mean = list()
    latencies_99 = list()
    lat_source = list()
    index = list()

    node_num = 1
    for nodes in [[args.src_node, args.dst_node, "Latency"]]:
        lat,timeline = calc_lat_inter(nodes[0],nodes[1],args)

        index.append(nodes[2].replace(r"\n", "\n"))

        topic_num = len(lat)
        if topic_num != 1:
            print("Error: the number of topic must be 1. ",nodes[2])
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

            lat_mean = list()
            lat_99 = list()
            lat_source = list()
            for j,(lat_name, time)  in enumerate(node_time.items(), start=1):
                    print(mean(time)/float(1e6))
                    lat_mean.append(mean(time)/float(1e6))
                    lat_99.append(np.percentile(time,99)/float(1e6))
                    lat_source.append(lat_name)

            latencies_mean.append(lat_mean)
            latencies_99.append(lat_99)

    fig, ax = plt.subplots()

    for l in calc_cb(args.dst_node,args).values():
        cb_mean = mean(l["Callback"])/float(1e6)
    latencies_mean[0].append(0)
    latencies_mean.append([ 0 for i in range(len(latencies_mean[0]))])
    latencies_mean[1][-1] = cb_mean

    print("cb / latency ", cb_mean/sum(latencies_mean[0]))

    index.append("Calllback")
    lat_source.append("")


    t_lat_mean = list(zip(*latencies_mean))
    t_lat_99 = list(zip(*latencies_99))
    x = np.arange(node_num+1)
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']



    width = 0.3
    #if args.nnpercentile:
    #    bot = np.array( [0] * node_num)
    #    for i,source_name in enumerate(lat_source):
    #        bar1 = ax.bar(x - width/2, t_lat_mean[i], width-0.03, bottom = bot, alpha = 0.9, hatch="xx", label=source_name, edgecolor='black')
    #        bot = bot + np.array(t_lat_mean[i])

    #    bot = np.array( [0] * node_num)
    #    for i,source_name in enumerate(lat_source):
    #        bar2 = ax.bar(x + width/2, t_lat_99[i], width-0.03, bottom = bot, color=colors[i], alpha = 0.9, hatch="..", edgecolor='black')
    #        bot = bot + np.array(t_lat_99[i])

    #    sublabel_y_pos = -0.03
    #    for rect in bar1:
    #        ax.text(rect.get_x() + rect.get_width()/2.0, sublabel_y_pos, "mean ", fontsize=15, ha="center")

    #    for rect in bar2:
    #        ax.text(rect.get_x() + rect.get_width()/2.0, sublabel_y_pos, "99th", fontsize=15, ha="center")

    #    ax.set_xticks(x)
    #    ax.set_xticklabels(index, fontsize=20)
    #    ax.tick_params(axis = 'x',pad=25)

    #else:
    bot = np.array( [0] * node_num)
    for i,source_name in enumerate(lat_source):
        ax.bar(x, t_lat_mean[i], width-0.03, bottom = bot, alpha = 0.9, label=source_name, edgecolor='black')
        bot = bot + np.array(t_lat_mean[i])
    ax.set_xticks(x)
    ax.set_xticklabels(index, fontsize=19)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(reversed(handles), reversed(labels),loc="best",fontsize=22)

    plt.xticks(rotation=0)
    plt.grid(axis='y')
    ax.set_axisbelow(True)

    plt.ylabel("Latency (ms)")

    plt.show()
