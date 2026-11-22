## Tracker code
## Once there is a GPS Fix it logs GPS coordinates and
## date-time information on the Pytrack's SD card.
## At boot it sends the board's SigFox ID to the SigFox network, where
## event callbacks can push data to a cloud backend for further processing.
## TODO:
## - Send GPS coordinates over SigFox (max 12 bytes, ~140 messages/day)
## - Since the board (Pycom's FiPy) supports also Lora and
##   LTE CAT M1 and NB-IOT, add auto switching in case SigFox isn't available
## - BLE / SmartPhone connectivity
## - Adafruit cloud, Mosquitto
##
## LED colours: red = booting, green = SigFox ID sent, blue = GPS fix

import socket, pycom, machine, sys, network, os, uos
import time, binascii, gc
from network import Sigfox
from machine import SD
from L76GNSS import L76GNSS
from pytrack import Pytrack

LOG_INTERVAL_S = 30   # seconds between two logged positions
FLUSH_EVERY = 10      # flush the log file every N positions

pycom.heartbeat(False)

# Reduce power consumption by switching off Wifi
wifi = network.WLAN()
wifi.deinit()

# Log onto the SD card; fall back to internal flash when there is no card.
# Append so a reboot doesn't wipe the previous session.
try:
    sd = SD()
    os.mount(sd, '/sd')
    log_path = '/sd/tracker.log'
except OSError as e:
    print('No usable SD card ({}), logging to flash instead'.format(e))
    log_path = '/flash/tracker.log'
f = open(log_path, 'a')

print("Running Python %s on %s" %(sys.version,  uos.uname() [4]))
f.write("## -->>> Starting new tracking log session on %s board with PyTrack shield.\n" %(uos.uname() [4]))
pycom.rgbled(0x7f0000) # red
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

# when the board starts we send the SigFox ID (8 hex characters)
s.send(binascii.hexlify(sigfox.id()))

# Sending message to SigFox network was successful
pycom.rgbled(0x007f00) # green

#Start GPS
py = Pytrack()
l76 = L76GNSS(py, timeout=600)
#start rtc
rtc = machine.RTC()
print('Acquiring GPS signal....')

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

# blue means we got GPS signal
pycom.rgbled(0x00007f) # blue

print('RTC Set from GPS to UTC:', rtc.now())
f.write("## -->>> Starting tracking at: {}\n".format(rtc.now()))
f.flush()

logged = 0
while (True):
    coord = l76.coordinates()
    if coord[0] is not None:
        print("$GPGLL>> {} at {}".format(coord, rtc.now()))
        f.write("{} - {}\n".format(coord, rtc.now()))
        logged += 1
        if logged % FLUSH_EVERY == 0:
            f.flush()
    time.sleep(LOG_INTERVAL_S)
