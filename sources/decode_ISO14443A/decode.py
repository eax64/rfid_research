#!/bin/python3

import argparse

SAMPLE_RATE = 28e6
NB_SAMPLE_READY = 4000

parser = argparse.ArgumentParser()
parser.add_argument('FILE', help='File to decode')
args = parser.parse_args()

data = open(args.FILE, "rb").read()    

i = 0
nb_on = 0
nb_off = 0
ready_for_data = False
data_len = len(data)

cur_raw_byte = []
all_bytes = []

def next_change_dist(current_state, max_seek):
    j = 0
    while i + j < data_len:
        if data[i+j] != current_state:
            return j
        if j > max_seek:
            break
        j += 1
    return max_seek
    

def raw_to_bitsymp(raw):
    seq = [r[0] for r in raw]
    seq_val = [r[1] for r in raw]
    if seq == [0, 1]:
        bitsymb = (0, "Z")

        # if abs(2.5e-6 - seq_val[0] / SAMPLE_RATE) > 0.5e-6:
        #     print("Pause of symb %s corrupted" % bitsymb[1])

    elif seq == [1, 0, 1]:
        bitsymb = (1, "X")
        
        if abs(64/13.56e6 - seq_val[0] / SAMPLE_RATE) > 0.116e-6:
            print("Symb %s corrupted" % bitsymb[1])

    elif seq == [1]:
        bitsymb = (0, "Y")
        
        # if abs(64/13.56e6 - seq_val[1] / SAMPLE_RATE) > 0.11e-6:
        #     print("Symb %s corrupted" % bitsymb[1])
    else:
        bitsymb = (0, "?")
        print("Symb not found")
        
    return bitsymb


while i < data_len:
    d = data[i]

    #
    # Part BEFORE being ready
    #
    
    while not d:
        i += 1
        if i >= data_len:
            break
        d = data[i]

    nb_on = 0
    while d:
        nb_on += 1
        i += 1
        if i >= data_len:
            break
        d = data[i]

    if nb_on > NB_SAMPLE_READY:
        ready_for_data = True
        print(nb_on)
        print("=" * 5 + " ready now sample nb %d (%.4fms) " % (i, i/SAMPLE_RATE*1e3) + "=" * 5)
    

    #
    # Part AFTER being ready
    #


    if ready_for_data:
        cnt_samples = 0
        start_of_com = False
        end_of_com = False
        no_information = False
        last_bitsymb = (-1, "?")
        bits = ""
        while not no_information:
    
            # Process pause
    
            
            nb_off = 0
            #print("0:%d" % cnt_samples)
            while not d:
                nb_off += 1
                i += 1
                if i >= data_len:
                    break
                d = data[i]
    
            if nb_off:
                if nb_off < SAMPLE_RATE * 2e-6:
                    print("Error, pause of %.2fus (%d samples) shorter than the minumum 2us" % (nb_off / SAMPLE_RATE * 1e6, nb_off))
                    break
                if nb_off > SAMPLE_RATE * 3.5e-6:
                    print("Error, pause of %.2fus (%d samples) longer than the maximum 3us" % (nb_off / SAMPLE_RATE * 1e6, nb_off))
                    break
                    
                cnt_samples += nb_off
                cur_raw_byte.append((0, nb_off, i/1000))
        
            # Process modulation
            
            nb_on = 0
            #print("1:%d" % cnt_samples)
            while d:
                nb_on += 1
                i += 1
                if i >= data_len:
                    break
                d = data[i]
    
                # if nb_on > 462 * 2:
                #     ready_for_data = False
                #     break
                if cnt_samples + nb_on >= SAMPLE_RATE * 9.4395e-6 and next_change_dist(1, 10) == 10:
                    break
    
            cnt_samples += nb_on
            cur_raw_byte.append((1, nb_on, i/1000))
    
            if cnt_samples + 10 >= SAMPLE_RATE * 9.4395e-6:
                cnt_samples = 0
                print(cur_raw_byte)
                
                bitsymb = raw_to_bitsymp(cur_raw_byte)
                print(bitsymb)


                if last_bitsymb[1] == "Y" and bitsymb[1] == "Y":
                    #if end_of_com and last_bitsymb[1] == "Y" and bitsymb[1] == "Y":
                    no_information = True
                    ready_for_data = False
                    cur_raw_byte = []
                    print("=" * 5 + " No information " + "=" * 5)
                    #break
                    #elif last_bitsymb[0] == 0 and bitsymb[1] == "Y":
                    end_of_com = True
                    if not start_of_com or not end_of_com:
                        bits = ""
                        print("=" * 5 + " No com " + "=" * 5)
                    else:
                        print("=" * 5 + " End of com " + "=" * 5)
                        print(bits)
                        if len(bits) == 8:
                            print("Short frame value: " + hex(int(bits[::-1], 2)))
                        else:
                
                            by = []
                            par = []
                            while bits:
                                tmp = bits[:8]
                                by.append("0x%02x" % int(tmp[::-1], 2))
                                bits = bits[8:]
                                if bits:
                                    par.append(int(bits[0]))
                                    bits = bits[1:]
                            print(by)
                            print(par)
                        bits = ""
                        print("=" * 15)
                    start_of_com = False
                    break
                
                elif bits == "" and not start_of_com:
                    if bitsymb[1] != "Z":
                        print("Curruption: Start of communication shall begin with a Z symb")
                    else:
                        start_of_com = True
                else:
                    bits += str(bitsymb[0])
            
                    
                last_bitsymb = bitsymb
                
                
                cur_raw_byte = []


    
