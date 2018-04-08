#Tracker
## Purpose
Build a device that tracks location and possibly other metrics and push them to the cloud. While a number of similar solutions already exist on the market, the focus of this one is to leverage Pycom's SiPy boards. 
Not only Pycom's SiPy boards are triple network capable (WiFi, SigFox and BLE) but they are also low power MicroPython enabled micro controllers.

## What's in the box
SiPy (or FiPy if there is support for LTE-CAT M1 / NB-IOT)
GPS
128x64 OLED display
3500mAh/3.8v Li-Po Battery
Li-Po Rider from Seed Studio
expansion board to update the firmware of your pycom baord. https://docs.pycom.io/chapter/datasheets/boards/expansion.html



## Step 1
Before you start make sure you use a proper USB cable if you do the following steps over serial/USB.
Upgrade the firmware of the Pycom Board: https://docs.pycom.io/chapter/gettingstarted/installation/firmwaretool.html
FiPy: 1.17.3.b1
Lora Region:Singapore (for local testing and can be forced / changed)
SigFox Region: New Zealand (Singapore and New Zealand are supported in the same region RC2+4)

## Upgrade the firmware of the PyTrack shield
https://docs.pycom.io/chapter/pytrackpysense/installation/firmware.html
PyTrack firmware version: 0.0.8


## Get Board Details
Use one of the IDE and Pycom's plugin to connect in REPL mode. I use the USB that is already connected to the board, you can also use IP if you chooose Wifi option.

```json
pymakr.conf
{
    "address": "/dev/cu.usbmodemPy343431",
    "username": "micro",
    "password": "python",
    "sync_folder": "",
    "open_on_start": true,
    "statusbar_buttons": [
        "console",
        "run",
        "upload",
        "download"
    ]
}
```

### Get your SigFox Id and PAC
Use the following sample code to show ID/PAC

```python
from network import Sigfox
import binascii
# initalise Sigfox for RCZ1 (You may need a different RCZ Region)
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ4)
# print Sigfox Device ID
print(binascii.hexlify(sigfox.id()))
# print Sigfox PAC number
print(binascii.hexlify(sigfox.pac()))
```
you should get results like these:
```shell
>>> print(binascii.hexlify(sigfox.id()))
b'004d53ea'
>>> print(binascii.hexlify(sigfox.pac()))
b'0ebfb82dc04b46e5'
```

SigFox : 4D53EA
SigFox PAC: 0EBFB82DC04B46E5

Now you can activate your SigFox enabled board with your board ID and PAC
Activation: https://backend.sigfox.com/activate

### Test SigFox network
While you are in REPL mode in your ide, enter the following code
```python
#send some data
import socket
#create a Sigfox socket 
s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
# make the socket blocking 
s.setblocking(True) 
# configure it as uplink only 
s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)  
# send some bytes 
s.send("Hello World")
```

You can see the result echo-ing:
```shell
>>> s.send("Hello World")
11
```

you can check the results in SigFox backedn web UI.
Messages are in Hex (convert them in ASCII: https://codebeautify.org/hex-string-converter)

