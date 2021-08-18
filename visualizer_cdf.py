import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from functools import reduce
import sys
import subprocess
from statistics import mean, variance, stdev, median_grouped

from visualizer_calc import *

def show_cdf(args):
    fig, ax = plt.subplots()
    for threads in args.threads:
        times = [ t / float(1e6) for t in calc_cdf(threads[0], args)]
        count, bins_count = np.histogram(times, bins=5000)

        pdf = count / sum(count)
        cdf = np.cumsum(pdf)

        x = np.append([0],bins_count[1:])
        y = np.append([0],cdf)
        ax.plot(x, y, label=threads[1], linewidth=2, color=threads[2])

    ax.legend(loc='lower right',fontsize=26)
    ax.set_xlabel("Runqueue Latency (ms)")
    ax.set_ylabel("CDF")

    ax.tick_params(axis='x', pad=10)
    ax.tick_params(axis='y', pad=10)
    if args.max != 0:
        plt.xlim(0,args.max)
    else:
        plt.xlim(0)
    plt.ylim(0,1)
    plt.grid()
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
