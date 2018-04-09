## Tracker code
## Once there is a GPS Fix it logs GSP coordinates and 
## date-time information on the Pytrack's SD card.
## It sends GPS coordinate to SigFox network where
## event callbacks will push this to Openshift Online Pro account
## for furthere processing. 
## TODO: 
## Since the board (Pycom's FiPy) supports also Lora and
## LTE CAT M1 and NB-IOT, I am planning to add code to support
## auto switching in case SigFox isn't available
## Look at adding support for 
##  - BLE / SmartPhone connectivity
##  - Adafruit cloud, Mosquitto
##  - etc..


from network import Sigfox
import socket
import machine
import math
import network
import os
import time
import utime
from machine import RTC
from machine import SD
from machine import Timer
from L76GNSS import L76GNSS
from pytrack import Pytrack
import struct
# setup as a station
 
import gc
 
time.sleep(2)
gc.enable()

# Instantiate SigFox class with the correct Zone. in this case Zone 4 works for both NZ and SG
# RCZ4: Feq: 920MHz, LPRS Module: eRIC-SIGFOX- RCZ4, countries:South America, Australia, New Zealand, Singapore and some parts of Asia
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ4)


#Start GPS
py = Pytrack()
l76 = L76GNSS(py, timeout=600)
#start rtc
rtc = machine.RTC()
print('Aquiring GPS signal....')
#try to get gps date to config rtc
while (True):
    gps_datetime = l76.get_datetime()
    #case valid readings
    if gps_datetime[3]:
        day = int(gps_datetime[4][0] + gps_datetime[4][1] )
        month = int(gps_datetime[4][2] + gps_datetime[4][3] )
        year = int('20' + gps_datetime[4][4] + gps_datetime[4][5] )
        hour = int(gps_datetime[2][0] + gps_datetime[2][1] )
        minute = int(gps_datetime[2][2] + gps_datetime[2][3] )
        second = int(gps_datetime[2][4] + gps_datetime[2][5] )
        print("Current location: {} {} ; Date: {}/{}/{} ; Time: {}:{}:{}".format(gps_datetime[0],gps_datetime[1], day, month, year, hour, minute, second))
        rtc.init( (year, month, day, hour, minute, second, 0, 0))
        break
 
print('RTC Set from GPS to UTC:', rtc.now())
 
chrono = Timer.Chrono()
chrono.start()
sd = SD()
os.mount(sd, '/sd')
f = open('/sd/tracker.log', 'w')
#create a Sigfox socket to send the GPS coordinate
s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
# make the socket blocking 
s.setblocking(True) 
# configure it as uplink only 
s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)  
gps_data = l76.get_datetime()
#s.send(gps_data[0])
s.send("1.275763")

while (True):
    print("RTC time : {}".format(rtc.now()))
    coord = l76.coordinates()
    print("$GPGLL>> {}".format(coord))
    f.write("{} - {}\n".format(coord, rtc.now()))