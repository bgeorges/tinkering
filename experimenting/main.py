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

machine.main('trk-sys.py')