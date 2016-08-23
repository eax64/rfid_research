#!/usr/bin/env python3

import string
import numpy
import matplotlib.pyplot as plt
import itertools
import instrument
import time
import os
from scipy import signal
import argparse

timescale = 5.e-03
timeoffset = 211.e-03
vscale = 2
trig_lvl = 2


o = instrument.RigolScope("/dev/usbtmc0")

def setup_oscilo():
    o.write(":TIM:SCAL %f" % timescale)
    o.write(":TIM:OFFS %f" % timeoffset)
    o.write(":CHAN1:SCAL %f" % vscale)
    o.write(":TRIG:EDG:SOUR CHAN1")
    o.write(":TRIG:EDG:LEV %d" % trig_lvl)
    o.write(":ACQ:MDEP 24000000")

def single_triger():
    o.write(":SINGLE")
    while o.wr(":TRIG:STAT?", 20) != b"WAIT\n":
        time.sleep(0.1)


def wait_and_save(nb dest):
    while o.wr(":TRIG:STAT?", 20) != b"STOP\n":
        time.sleep(0.1)

    o.write(":WAV:FORM BYTE")
    o.write(":WAV:MODE RAW")

    print("YINC -> ", o.wr(":WAV:YINC?", 20))

    CHUNK_SIZE = 250000 * 4
    data = numpy.array([], "B")
    while len(data) < 24e6:
        i_from = len(data) + 1
        i_to = len(data) + CHUNK_SIZE
        if i_to > 24e6:
            i_to = 24e6
        o.write(":WAV:STAR %d" % i_from)
        o.write(":WAV:STOP %d" % i_to)
        o.write(":WAV:DATA?")
        rawdata = o.read(CHUNK_SIZE)
        print("rcv:", len(rawdata))
        if len(rawdata) < CHUNK_SIZE:
            print(rawdata)
        data = numpy.append(data, numpy.frombuffer(rawdata, 'B'))
        time.sleep(0.01)
        print("total", len(data))
        print("%.2f" % (len(data) / 24e6 * 100))
        numpy.save("%s/%d" % (dest, nb), data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dest', required=True, help='Destination directory for samples')
    parser.add_argument('--cmd', required=True, help='Command to run that will trigger the scope')
    args = parser.parse_args()
    
    for nb in range(500):
        print("Sample nb: %d" % nb)
        setup_oscilo()
        single_triger()
        os.system(args.cmd)
        wait_and_save(nb, args.dest)
        time.sleep(0.2)
