## 

import socket, pycom, machine, sys, network, os, uos
import math, time, utime, struct, binascii, gc
from network import Sigfox
from machine import Timer

pycom.heartbeat(False)

print("Running Python %s on %s" %(sys.version,  uos.uname() [4]))
pycom.rgbled(0x7f0000) #yellow
time.sleep(2)
gc.enable()

# Instantiate SigFox class with the correct Zone. in this case Zone 4 works for both NZ and SG
# RCZ4: Feq: 920MHz, LPRS Module: eRIC-SIGFOX- RCZ4, countries:South America, Australia, New Zealand, Singapore and some parts of Asia
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ4)
#create a Sigfox socket to send the GPS coordinate
s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
# make the socket blocking 
s.setblocking(True) 
# configure it as uplink only 
s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)

# when the board starts we send the SigFox ID
s.send("{}".format(binascii.hexlify(sigfox.id())))

print(binascii.hexlify(sigfox.id()))

# Blue this time
pycom.rgbled(0x0000ff)