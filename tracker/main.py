## Test code for read date/time from gps and update RTC
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
s.send("GPS Fixed")

while (True):

    print("RTC time : {}".format(rtc.now()))
    coord = l76.coordinates()
    f.write("{} - {}\n".format(coord, rtc.now()))
    print("$GPGLL>> {}".format(coord))
    coord1 = l76.coordinates1()
    print("$GPGGA>> {}".format(coord1))
    coord2 = l76.get_datetime()
    print("$GPRMC>> {}".format(coord2))