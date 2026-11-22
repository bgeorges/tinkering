# Sandbox
A place where I keep successful experiments with the FiPy board, before they make it into the tracker.
Open this folder as its own Pymakr project and run a single file with *Run*.

| File | What it tests |
|---|---|
| `led_test.py` | Cycles the on-board RGB LED. |
| `sigfox_id.py` | Opens a SigFox socket (zone RCZ4) and sends/prints the board's SigFox ID. |
| `oled_test.py` | Drives a 128x64 SSD1306 OLED over I2C on pins G16 (SDA) / G17 (SCL). |
| `writer.py` | Peter Hinch's text renderer for framebuffer displays (MIT), used by `oled_test.py`. |

`oled_test.py` also needs two files that are not in this repo; upload them next to it:
- `ssd1306.py`: the SSD1306 driver from the MicroPython repository (`drivers/display/ssd1306.py`).
- `freesans20.py`: a font generated with Peter Hinch's `micropython-font-to-py`.
