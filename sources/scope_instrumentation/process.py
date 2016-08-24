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

if __name__ == "__main__":


    plt.rcParams['agg.path.chunksize'] = 10000
    
    parser = argparse.ArgumentParser()
    parser.add_argument('FILE', help='File to process')
    parser.add_argument('--out', default="out.png", help='Output filename')
    parser.add_argument('--quick', action="store_true", help='Draft image')
    parser.add_argument('--full', default=False, action="store_true", help='Does not half the signal')
    parser.add_argument('--from', dest="frm", default=0, type=float, help='Display from offset (ms)')
    parser.add_argument('--to', default=192, type=float, help='Display to offset (ms)')
    parser.add_argument('--input_data_duration', default=192, type=int, help='Duration (in ms) of the input data')
    parser.add_argument('--decimation', default=3, type=int, help='Decimation of the input data')
    args = parser.parse_args()

    data_duration = args.to - args.frm
    

    data = numpy.load(args.FILE)
    print("Numpy file loaded")

    data_size = len(data)

    nb_idx_per_ms = data_size / args.input_data_duration
    from_idx = int(args.frm * nb_idx_per_ms)
    to_idx = int(args.to * nb_idx_per_ms)

    print("len bef:", data_size)
    data = data[from_idx:to_idx]
    print("len aft:", len(data))
    
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

    print("Drawing image")
    figsize=(20,5)
    if not args.quick:
        figsize=(30,5)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)


    dpi = 50
    if not args.quick:
        dpi = 220
        ax.set_xlabel('time (ms)')
        ax.set_ylabel('voltage (V)')

        tick = data_duration / 100
        
        ax.set_xlim(0, data_duration)
        ax.set_xticks(numpy.arange(0, data_duration, tick))
        ax.set_xticklabels(numpy.arange(args.frm, args.to, tick), rotation=45, fontsize=7)
        
        ax.grid()


    ax.plot(numpy.linspace(0, data_duration, num=data_size), data)

    plt.savefig(args.out, bbox_inches='tight', dpi=dpi)
    print("Output saved in %s" % args.out)
