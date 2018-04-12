# ACKed
# got the right SDA/SDC pin mapping between the Fi/SiPy boards (pins G16 and G17) 
# and the SSD1306 OLED display
import machine, sys, pycom, os, time, uos, gc, ssd1306
from ssd1306 import SSD1306_I2C
from writer import Writer

# fonts
import freesans20


pycom.heartbeat(False)

print("Running Python %s on %s" %(sys.version,  uos.uname() [4]))
# Red
pycom.rgbled(0x7f0000)
time.sleep(2)
gc.enable()
 
i2c = machine.I2C(0, pins=('G16','G17'))
oled = SSD1306_I2C(128, 64, i2c)
print(i2c.scan())
oled.pixel(0, 0, 1)
oled.show()
oled.fill(0)

oled.show()
oled.fill(1)
oled.show()

# green
pycom.rgbled(0x00ff00)


