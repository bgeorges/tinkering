# Tracker
## Purpose
Build a device that tracks location and possibly other metrics and push them to the cloud. While a number of similar solutions already exist on the market, the focus of this one is to leverage Pycom's SiPy boards. 
Not only Pycom's SiPy boards are triple network capable (WiFi, SigFox and BLE) but they are also low power MicroPython enabled micro controllers.


## Layout
| Path | What |
|---|---|
| `device/` | Code uploaded to the board: `boot.py`, `main.py` (the tracker) and `lib/` (Pytrack + GPS drivers). `pymakr.conf` syncs only this folder. |
| `sandbox/` | One-off hardware experiments (OLED, SigFox ID, LED). Open it as its own Pymakr project. |

## What it does
1. Switches WiFi off to save power and opens `tracker.log` on the SD card (or `/flash` if there is no card), appending to it.
2. Sends the board's SigFox ID once at boot. LED: red → green.
3. Waits for a GPS fix and sets the RTC to UTC from it. LED: blue.
4. Logs the position every 30 s (`LOG_INTERVAL_S` in `main.py`).

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
It prints the 8-character device ID and the 16-character PAC.
Keep the PAC private: it is the one-time code that registers the board to an account.

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

note: For a 12-byte data payload, a Sigfox frame will use 26 bytes in total. The payload allowance in downlink messages is 8 bytes.

### GPS
Get the Pytrack libraries from https://docs.pycom.io/chapter/pytrackpysense/installation/libraries.html
`device/lib/L76GNSS.py` is a modified version of Pycom's library that also parses
GNGGA/GNRMC sentences, so `get_datetime()` returns the UTC date and time used to set the RTC.

