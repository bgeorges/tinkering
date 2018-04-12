## Tracker code
## Once there is a GPS Fix it logs GSP coordinates and 
## date-time information on the Pytrack's SD card.
## It sends GPS coordinate to SigFox network where
## event callbacks will push this to Openshift Online Pro account
## for further processing. 
## TODO: 
## Since the board (Pycom's FiPy) supports also Lora and
## LTE CAT M1 and NB-IOT, I am planning to add code to support
## auto switching in case SigFox isn't available
## Look at adding support for 
##  - BLE / SmartPhone connectivity
##  - Adafruit cloud, Mosquitto
##  - etc..

import socket, pycom, machine, sys, network, os, uos
import math, time, utime, struct, binascii, gc

pycom.heartbeat(False)

# Reduce power consumption by switching off Wifi
wifi = network.WLAN()
wifi.deinit()

# Logging data onto the SD Card
# TODO: add some error checking here for when no SD Card is present or full or file permission error, etc..
sd = SD()
os.mount(sd, '/sd')
f = open('/sd/tracker.log', 'w')

print("Running Python %s on %s" %(sys.version,  uos.uname() [4]))
pycom.rgbled(0x7f0000) #yellow
time.sleep(2)
gc.enable()

# blue means we got GPS signal
pycom.rgbled(0x00007f) # blue

print('RTC Set from GPS to UTC:', rtc.now())
f.write("## -->>> Starting tracking at: ", rtc.now() ) 