#!/usr/bin/env python3

import numpy
import matplotlib
# matplotlib.use('Agg')
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import argparse
import itertools
from scipy import signal
import matplotlib.ticker as tkr

def remove_lower_half(x):
    if x < 0:
        return 0
    return x

def get_data(args, frm, to):
    

    data = numpy.load(args.FILE)
    print("Numpy file loaded")

    data_size = len(data)

    nb_idx_per_ms = data_size / args.input_data_duration
    from_idx = int(frm * nb_idx_per_ms)
    to_idx = int(to * nb_idx_per_ms)

    print("len loaded:", data_size)
    data = data[from_idx:to_idx]
    print("len after selection:", len(data))
    
    data = signal.decimate(data, args.decimation)
    data_size = len(data)

    #Center to 0
    avg = numpy.average(data)
    data = data - avg

    if not args.full:
        print("Halfing signal")
        vfunc = numpy.vectorize(remove_lower_half)
        data = vfunc(data)

    #Convert to a readable unit
    data = data * 10*1.057031e-01/255*100

    return data, data_size

def generate_plot(args, data, data_size, frm, to, ax):
    print("Ploting image")

    if not args.quick:
        ax.set_xlabel('time (ms)')
        ax.set_ylabel('voltage (V)')

        tick = data_duration / 100
        
        ax.set_xlim(0, data_duration)
        ax.set_xticks(numpy.arange(0, data_duration, tick))
        ax.set_xticklabels(numpy.arange(frm, to, tick), rotation=45, fontsize=7)
        
        ax.grid()

    ax.plot(numpy.linspace(0, data_duration, num=data_size), data)


if __name__ == "__main__":


    plt.rcParams['agg.path.chunksize'] = 10000
    
    parser = argparse.ArgumentParser()
    parser.add_argument('FILE', help='File to process')
    parser.add_argument('--out', default="out.png", help='Output filename')
    parser.add_argument('--quick', action="store_true", help='Draft image')
    parser.add_argument('--full', default=False, action="store_true", help='Does not half the signal')
    parser.add_argument('--ranges', default="0:190", help='Display ranges (in ms) ex "10.1:11 12:13"')
    parser.add_argument('--to', default=192, type=float, help='Display to offset (ms)')
    parser.add_argument('--input_data_duration', default=192, type=int, help='Duration (in ms) of the input data')
    parser.add_argument('--decimation', default=3, type=int, help='Decimation of the input data')
    args = parser.parse_args()

    rngs = args.ranges.split(" ")
    n_plot = len(rngs)
    figsize=(20, 5 * n_plot)
    if not args.quick:
        figsize=(30, 5 * n_plot)
    
    fig, axs = plt.subplots(n_plot, figsize=figsize)
    if n_plot == 1:
        axs = [axs]
    for i,rng in enumerate(rngs):
        frm,to = map(float, rng.split(":"))
        data_duration = to - frm
        data, data_size = get_data(args, frm, to)
        generate_plot(args, data, data_size, frm, to, axs[i])

    dpi = 50
    if not args.quick:
        dpi = 220

    print("Drawing image")
    plt.savefig(args.out, bbox_inches='tight', dpi=dpi)
    print("Output saved in %s" % args.out)
