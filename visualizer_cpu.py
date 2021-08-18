import matplotlib.pyplot as plt
from scipy.stats import norm
from functools import reduce
import sys
import subprocess
from statistics import mean, variance, stdev, median_grouped

from visualizer_calc import *

plt.rcParams['figure.subplot.top'] = 0.88

def show_cpu(args):
    fig, ax = plt.subplots(figsize=(16,10))

    major_ticks = range(args.cpu_num)
    minor_ticks = range(args.cpu_num)
    ax.set_yticks(major_ticks)
    ax.set_yticklabels(major_ticks)
    ax.set_yticks(minor_ticks, minor=True)

    for thread in args.threads:
        time, cpu = calc_cpu(thread[0],args)
        time_ = [ t / float(1e9)  for t in time ]
        cpu_ = [ c + float(thread[3]) for c in cpu ]
        ax.scatter(time_, cpu_, label =thread[1], rasterized=True)

    ax.set_ylabel('Processor ID')
    ax.set_xlabel('Elapsed Time (s)')
    ax.grid(axis="y")
    ax.grid(axis="y",which="minor")
    ax.set_axisbelow(True)
    ax.legend(loc="center",bbox_to_anchor=(0.5,1.1), ncol=4, markerscale=2.0, fontsize=22)

    plt.show()
