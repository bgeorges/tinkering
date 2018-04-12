import socket, pycom, machine, sys, network, os, uos
import math, time, utime, struct, binascii, gc

pycom.heartbeat(False)

print("Running Python %s on %s" %(sys.version,  uos.uname() [4]))
pycom.rgbled(0x7f0000) #yellow
time.sleep(2)
gc.enable()

# blue means we got GPS signal
pycom.rgbled(0x00007f) # blue

print('RTC Set from GPS to UTC:', time.time())