import matplotlib.pyplot as plt
import argparse
from statistics import mean, variance, stdev, median_grouped

plt.rcParams['font.family'] ='sans-serif'
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['font.size'] = 30
plt.rcParams['xtick.labelsize'] = 17
plt.rcParams['ytick.labelsize'] = 20
plt.rcParams['axes.linewidth'] = 1.0

from visualizer_hist import *
from visualizer_stack import *
from visualizer_timeline import *
from visualizer_cdf import *
from visualizer_cpu import *

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_inter = subparsers.add_parser('inter')
parser_inter.add_argument("src_node", metavar="<src node>")
parser_inter.add_argument("dst_node", metavar="<dst node>")
parser_inter.add_argument("--ros-detail", dest="ros_detail", action='store_true')
parser_inter.add_argument("-c", dest="concat", action='store_true')
parser_inter.set_defaults(handler=show_inter)

parser_intra = subparsers.add_parser('intra')
parser_intra.add_argument("node", metavar="<node>")
parser_intra.add_argument("--ros-detail", dest="ros_detail", action='store_true')
parser_intra.add_argument("-c", dest="concat", action='store_true')
parser_intra.set_defaults(handler=show_intra)

parser_stack = subparsers.add_parser('stack')
parser_stack.add_argument("--nodes", "-n", metavar=("src","dst","name"), nargs=3, action="append", required=True)
parser_stack.add_argument("--ros-detail", dest="ros_detail", action='store_true')
parser_stack.add_argument("--99th-percentile", "-99th", dest="nnpercentile", action='store_true')
parser_stack.set_defaults(handler=show_stack)

parser_stack_comp_cb = subparsers.add_parser('stack_comp_cb')
parser_stack_comp_cb.add_argument("src_node", metavar="<src node>")
parser_stack_comp_cb.add_argument("dst_node", metavar="<dst node>")
parser_stack_comp_cb.add_argument("--ros-detail", dest="ros_detail", action='store_true')
parser_stack_comp_cb.set_defaults(handler=show_stack_comp_cb)

parser_timeline = subparsers.add_parser('timeline')
parser_timeline.add_argument("src_node", metavar="<src node>")
parser_timeline.add_argument("dst_node", metavar="<dst node>")
parser_timeline.add_argument('--kernel', dest='pickup', action='append_const', const="Kernel")
parser_timeline.add_argument('--pubq', dest='pickup', action='append_const', const="Pub. Queue")
parser_timeline.add_argument('--subq', dest='pickup', action='append_const', const="Sub. Queue")
parser_timeline.add_argument('--nw', default="")
parser_timeline.set_defaults(handler=show_timeline)

parser_cdf = subparsers.add_parser('cdf')
parser_cdf.add_argument("--threads", "-t", metavar=("name","title", "color"), nargs=3, action="append", required=True)
parser_cdf.add_argument('--max', default=0., type=float)
parser_cdf.set_defaults(handler=show_cdf)

parser_cpu = subparsers.add_parser('cpu')
parser_cpu.add_argument("cpu_num", type=int)
parser_cpu.add_argument("--threads", "-t", metavar=("name","title", "color", "offset"), nargs=4, action="append", required=True)
parser_cpu.add_argument('--max', default=0., type=float)
parser_cpu.set_defaults(handler=show_cpu)

args = parser.parse_args()
if hasattr(args, 'handler'):
    args.handler(args)
else:
    print("Command line parse error")
