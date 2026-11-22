# tinkering

Experimenting with IoT, Home Automation, RF, and more...

Each folder is an independent hobby project with its own hardware, language and README.
They share nothing except this repository.

| Project | Hardware | Stack | Status |
|---|---|---|---|
| [`relay-controller/`](relay-controller/) | Raspberry Pi 2 + 4-channel relay board | Node.js / Express, `rpio` | REST API to switch relays on/off (2018) |
| [`tracker/`](tracker/) | Pycom FiPy/SiPy + PyTrack shield | MicroPython | GPS tracker that logs to SD card and reports over SigFox (2018, prototype) |
| [`experimenting/`](experimenting/) | Pycom FiPy + SSD1306 OLED | MicroPython | Test ground for board experiments, e.g. OLED and GPS (2018) |
| [`bsd/`](bsd/) | Arduino Yun + NeoPixel matrix + buzzer | Arduino (C++) | "BullShit detector": web button that triggers lights and an alarm (2016) |

## Layout conventions

- One folder per project, each with its own `README`.
- Stack-specific ignore rules live in the project's own `.gitignore`; the root `.gitignore` only holds shared rules.
- MicroPython board libraries live in `<project>/lib/` and are committed.

## License

[MIT](LICENSE)
