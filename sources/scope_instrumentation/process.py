#!/usr/bin/env python3

import numpy
import matplotlib
# matplotlib.use('Agg')
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import argparse
import itertools
from scipy import signal

def remove_lower_half(x):
    if x < 0:
        return 0
    return x

if __name__ == "__main__":


    plt.rcParams['agg.path.chunksize'] = 10000
    
    parser = argparse.ArgumentParser()
    parser.add_argument('FILE', help='File to process')
    parser.add_argument('--quick', action="store_true", help='Draft image')
    args = parser.parse_args()

    data = numpy.load(args.FILE)
    print("Numpy file loaded")

    deci = 3
    data = signal.decimate(data, deci)
    data_size = len(data)

    #Center to 0
    avg = numpy.average(data)
    data = data - avg

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
        dpi = 200    
        ax.set_xlabel('time (ms)')
        ax.set_ylabel('voltage (V)')
        ax.set_xlim(0, 200)
        ax.set_xticks(numpy.arange(0, 200, 1))
        ax.set_xticklabels(numpy.arange(0, 200, 1), rotation=45, fontsize=7)
        ax.grid()


    ax.plot(numpy.linspace(0, 192, num=data_size), data)

    plt.savefig('out.png', bbox_inches='tight', dpi=dpi)
