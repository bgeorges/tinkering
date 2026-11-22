# ACKed
# 
import pycom, machine, sys, os, uos, gc, time
pycom.heartbeat(False)

print("Running Python %s on %s" %(sys.version,  uos.uname() [4]))
# Red
pycom.rgbled(0x7f0000)
time.sleep(2)
gc.enable()

# blue
pycom.rgbled(0x00007f)
time.sleep(2)

# Red
pycom.rgbled(0xff0000)
time.sleep(2)

# Green
pycom.rgbled(0x00ff00)

