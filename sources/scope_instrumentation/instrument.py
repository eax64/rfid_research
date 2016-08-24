import os
 
class usbtmc:
    """Simple implementation of a USBTMC device driver, in the style of visa.h"""
 
    def __init__(self, device):
        self.device = device
        self.FILE = os.open(device, os.O_RDWR)
 
    def write(self, command):
        os.write(self.FILE, command);
 
    def read(self, length = 4000):
        return os.read(self.FILE, length)
 
    def sendReset(self):
        self.write(b"*RST")
 
 
class RigolScope:
    """Class to control a Rigol DS1000 series oscilloscope"""
    def __init__(self, device):
        self.meas = usbtmc(device)
 
    def write(self, command):
        """Send an arbitrary command directly to the scope"""
        self.meas.write(bytes(command, "utf8"))
 
    def read(self, command):
        """Read an arbitrary amount of data directly from the scope"""
        return self.meas.read(command)

    def wr(self, c1, c2):
        self.write(c1)
        return self.read(c2)
