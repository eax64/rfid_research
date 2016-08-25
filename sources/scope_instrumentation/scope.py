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
import io
from PIL import Image

timescale = 5.e-03
timeoffset = 290.e-03
vscale = 10
trig_lvl = 5


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

def save_screen(dest, nb):
    o.write(":DISP:DATA?")
    data = o.read(2).decode("utf8")
    # assert(data[0] == "#")
    data = o.read(int(data[1]))
    rawdata = o.read(int(data, 10))
    Image.open(io.BytesIO(rawdata)).save("%s/%d.png" % (dest, nb))

def wait_and_save(nb, dest):
    print("wait and save")
    while o.wr(":TRIG:STAT?", 20) != b"STOP\n":
        time.sleep(0.1)
    print("Ok Trigered")

    o.write(":WAV:FORM BYTE")
    o.write(":WAV:MODE RAW")

    print("YINC -> ", o.wr(":WAV:YINC?", 20))

    CHUNK_SIZE = 250000 * 3
    data = numpy.array([], "B")
    while len(data) < 24e6:
        i_from = len(data) + 1
        i_to = len(data) + CHUNK_SIZE
        if i_to > 24e6:
            i_to = 24e6
        print("from %d to %d" % (i_from, i_to))
        o.write(":WAV:STAR %d" % i_from)
        o.write(":WAV:STOP %d" % i_to)
        o.write(":WAV:DATA?")

        data_size = o.read(2).decode("utf8")
        print(data_size)
        # assert(data[0] == "#")
        data_size = o.read(int(data_size[1]))
        print(data_size)
        rawdata = o.read(int(data_size, 10))


        print("rcv:", len(rawdata))
        if len(rawdata) < CHUNK_SIZE:
            print(rawdata)
        data = numpy.append(data, numpy.frombuffer(rawdata, 'B'))
        time.sleep(0.1)
        print("total", len(data))
        print("Progression: %.2f" % (len(data) / 24e6 * 100))
    numpy.save("%s/%d" % (dest, nb), data)
    save_screen(dest, nb)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--dest', required=True, help='Destination directory for samples')
    parser.add_argument('--cmd', required=True, help='Command to run that will trigger the scope')
    parser.add_argument('--time', help='Timeoffset')
    parser.add_argument('--repeat', default=150, type=int, help='Number of repeat')
    args = parser.parse_args()

    if args.time:
        timeoffset = float(args.time) * 1e-03
    
    for nb in range(args.repeat):
        try:
            print("Sample nb: %d" % nb)
            print("setup")
            setup_oscilo()
            print("prepare triger")
            single_triger()
            print("run cmd")
            os.system(args.cmd)
            print("wait and save")
            wait_and_save(nb, args.dest)
            time.sleep(1)
        except Exception as e:
            print(e)

