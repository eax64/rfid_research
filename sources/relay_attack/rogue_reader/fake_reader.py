#!/usr/bin/python

import time
import rfidiot
import sys
import os
import fcntl
import select

try:
        card= rfidiot.card
except:
        print "Couldn't open reader!"
        os._exit(True)

def send(apdu):
        ret = card.pcsc_send_apdu(apdu)
        if card.errorcode != "FFFF":
                return card.data + card.errorcode
        else:
                return card.data

while not card.uid:
        card.select()
        time.sleep(0.1)
print(card.uid)


fifo_from_fake_reader = os.open("/tmp/to_real_card", os.O_RDONLY)
fifo_to_fake_reader = os.open("/tmp/from_real_card", os.O_WRONLY)

print(".")
while True:
        is_readable = [fifo_from_fake_reader]
        is_writable = [fifo_to_fake_reader]
        is_error = []
        r, w, e = select.select(is_readable, is_writable, is_error)
        if r:

                data = os.read(r[0], 1024)
                data = data.encode("hex").upper()
                data = [data[i:i+2] for i in range(0, len(data), 2)]
                out = send(data)
                
                # time.sleep(0.01)
                os.write(fifo_to_fake_reader, out.decode("hex"))
                

                if not data:
                        print("closed")
                        break
                print(">", data)
                print("<", out)
