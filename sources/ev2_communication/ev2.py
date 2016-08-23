import time
import rfidiot
import sys
import os
import hashlib, binascii
from Crypto.Hash import CMAC
from Crypto.Cipher import AES

try:
    card = rfidiot.card
except:
    print("Couldn't open reader!")
    os._exit(True)

key = 16*'\x00'
iv = 16*'\x00'
cipher = AES.new(key, AES.MODE_CBC, iv)

def send(apdu, debug=False):
    if debug:
        print(">>> " + str(apdu))
    if card.readertype == card.READER_LIBNFC:
        ret = card.nfc.sendAPDU(apdu)
        ret = ret[1]
    elif card.readertype == card.READER_PCSC:
        ret = card.pcsc_send_apdu(apdu)
        if card.errorcode != "FFFF":
            ret = card.data + card.errorcode
        else:
            ret = card.data
    else:
        exit("Reader type %d not supported" % card.READER_ACG)

    if debug:
        print("<<< " + str(ret))
    return ret

def splitBytes(data):
    """Split 'AABBCC' into ['AA', 'BB', CC']"""
    return [data[i:i+2] for i in range(0, len(data), 2)]

def interlacing(data1, data2, nb_elem, size_elem):
    ret = []
    for i in range(nb_elem):
        ret += data1[i*size_elem:(i+1)*size_elem] + data2[i*size_elem:(i+1)*size_elem]
    return ret

def waitForCardPresent():
    """Loop until a card is present"""
    while not card.uid:
        card.select()
        time.sleep(0.1)


def displayCardInfo():
    """Check App ISO FIle ID and AID"""
    idx = 1
    appdata = send(["6D"])
    hasmore = True
    while hasmore:
        print("%s Entry %d %s" % ("#"*5, idx, "#"*5)) 
        print("AID: %s" % appdata[2:8])
        print("isofileID: %s" % appdata[8:12])
        print("DFname: %s" % appdata[12:])
        hasmore = appdata[:2] == "AF"
        idx += 1
        if hasmore:
            appdata = send(["AF"])

def selectCardByDFname(dfname):
    """select the virtual app by selecting the ISOfile VIID (DFname)"""
    selectDF = ["00", "A4", "04", "00", "%02d" % len(dfname)] + dfname +  ["00"]
    isoselectresp = send(selectDF)
    if isoselectresp != "9000":
        print("Error selecting app. Resp: %s" % isoselectresp)

        
def createApp():
    """Create the app. Use only one time"""
    createapp = ["CA", "44", "44", "77", "0F", "9E", "06", "04", "00", "02", "18", "06", "77", "77"]
    send(createapp)

def preparePC():
    """Send the preparePC command"""
    data_prepare_pc = send(["F0"], True)
    data_prepare_pc = splitBytes(data_prepare_pc)

    option = data_prepare_pc[1]
    pubresp = data_prepare_pc[2:4]
    PPS1 = data_prepare_pc[4]
    return {"option": option, "pubresp": pubresp, "PPS1": PPS1}

def proximityCheck(nb_exchange, bytevect):
    """send 1 < n < 8 rounds of apdu prox check with n being a number of
    1-8 byte exchanges not exceeding 8 bytes over all transactions"""

    assert(nb_exchange in [1, 2, 4, 8])
    nb_bytes = 8 / nb_exchange
    
    data_prox_check = []
    for i in range(nb_exchange):
	proxAPDU = ["F2", "%02d" % nb_bytes] + bytevect[i*nb_bytes:(i+1)*nb_bytes]
	ret_APDU =  send(proxAPDU, True)
	data_prox_check.append(ret_APDU)
    return splitBytes("".join(data_prox_check))

def verifyPC(prox_check_data, bytevect, preparePC_data, nb_exchange):
    
    preMAC_data = [
        preparePC_data["option"],
        preparePC_data["pubresp"][0],
        preparePC_data["pubresp"][1],
        preparePC_data["PPS1"]
    ]

    nb_bytes = 8 / nb_exchange
    preMAC_data += interlacing(prox_check_data, bytevect, nb_exchange, nb_bytes)
    print(preMAC_data)
    preMAC_reader_data = ["FD"] + preMAC_data
    verbytes = bytearray(int(x,16) for x in preMAC_reader_data)

    readerMAC = CMAC.new(key, ciphermod=AES)
    readerMAC.update(bytes(verbytes))
    print("reader MAC:\t%s\n" % readerMAC.hexdigest())

    auth_data = ["FD"] + splitBytes(binascii.hexlify(readerMAC.digest()[1::2]))
    data_auth_check = send(auth_data, True)
    data_auth_check = splitBytes(data_auth_check)

    auth_bytes = bytearray(int(x,16) for x in data_auth_check[1:])

    preMAC_card_data = ["90"] + preMAC_data
    cardbytes = bytearray(int(x,16) for x in preMAC_card_data)
    
    cardauth = CMAC.new(key, ciphermod=AES)
    cardauth.update(str(cardbytes))

    print("\ncard MAC:\t" + cardauth.hexdigest())
    cardauthconcat = binascii.hexlify(cardauth.digest()[1::2])

    print("\nLocal CMAC:\t" + cardauthconcat)
    print("Remote CMAC:\t" + binascii.hexlify(auth_bytes))

    print("")
    # locally check that the values match. PCD MUST disengage if they do not!
    if cardauthconcat == binascii.hexlify(auth_bytes):
	print("%sThe message from VC is authentic%s" % ("\033[92m", "\033[0m"))
    else:
	print("%sThe message or the key is wrong%s" % ("\033[91m", "\033[0m"))


def checkIfLocked():
    """Test whether an unrelated auth command works. If response is longer than 2 bytes and prepended with "AF" it works."""

    auth_atmpt = send(["AA", "01"], True)
    auth_atmpt = splitBytes(auth_atmpt)

    print("")
    if auth_atmpt[0] == "AF":
        print("%sOk.%s" % ("\033[92m", "\033[0m"))
    else:
        print("%s/!\ FAIL. The card have been soft locked.%s" % ("\033[91m", "\033[0m"))


if __name__ == "__main__":
    bytevect = ["AA", "BB","CC", "DD", "EE", "FF", "00", "11"]
    
    waitForCardPresent()
    # displayCardInfo()
    selectCardByDFname(["02", "18", "06", "77", "77"])

    print("===\tPrepare PC\t===\n")
    preparePC_data = preparePC()

    print("\n===\tProximity Check\t===\n")
    nb_exchange = 1
    proximity_check_data = proximityCheck(nb_exchange, bytevect)
        
    print("\n===\tVerify PC\t===\n")
    verifyPC(proximity_check_data, bytevect, preparePC_data, nb_exchange)

    print("\n===\tCheck locked\t===\n")
    checkIfLocked()
