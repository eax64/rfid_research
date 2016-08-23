#!/usr/bin/env python3

import numpy
import matplotlib
# matplotlib.use('Agg')
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import argparse
import itertools
from scipy import signal
import scipy.ndimage as im

# from galry import *
#from numpy.random import randn


def remove_lower_half(x):
    if x < 0:
        return 0
    return x

if __name__ == "__main__":


    plt.rcParams['agg.path.chunksize'] = 10000
    # print(plt.rcParams)
    # exit()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('FILE', help='File to process')
    args = parser.parse_args()

    data = numpy.load(args.FILE)
    print("loaded")

    # fd = open("data_raw_float",'wb')
    # fd.write(data.astype('float32').tobytes())
    # fd.close()

    data = signal.decimate(data, 4)
    avg = numpy.average(data)
    data = data - avg
    

    # avg = numpy.average(data)
    # print(avg, rms, max(data), min(data))

    # data = im.median_filter(data, 1)
    print("halfing")
    vfunc = numpy.vectorize(remove_lower_half)
    data = vfunc(data)

    print("rms")
    rms = numpy.linalg.norm(data)/numpy.sqrt(len(data))

    print("max")
    mx = max(data)
    print(rms, min(data), mx)

    print("fig")
    plt.figure(figsize=(20,6), dpi=10)
    print("y")
    plt.ylim((rms*2, mx))
    plt.plot(data)
    plt.savefig('out.png')
