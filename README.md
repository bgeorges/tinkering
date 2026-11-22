# tinkering

Experimenting with IoT, Home Automation, RF, and more...

Each folder is an independent hobby project with its own hardware, language and README.
They share nothing except this repository.

| Project | Hardware | Stack | Status |
|---|---|---|---|
| [`relay-controller/`](relay-controller/) | Raspberry Pi 2 + 4-channel relay board | Node.js / Express, `rpio` | REST API to switch relays on/off (2018) |
| [`tracker/`](tracker/) | Pycom FiPy/SiPy + PyTrack shield | MicroPython | **Unsupported.** GPS tracker that logs to SD card and reports over SigFox, plus a `sandbox/` of board experiments (2018). Final snapshot: [`tracker-v1.0.0`](https://github.com/bgeorges/tinkering/releases/tag/tracker-v1.0.0). Continued as [lorawan-tracker](https://github.com/bgeorges/lorawan-tracker). |
| [`bsd/`](bsd/) | Arduino Yun + NeoPixel matrix + buzzer | Arduino (C++) | "BullShit detector": web button that triggers lights and an alarm (2016) |

## Layout conventions

- One folder per project, each with its own `README`.
- Stack-specific ignore rules live in the project's own `.gitignore`; the root `.gitignore` only holds shared rules.
- MicroPython board libraries live in `lib/` next to the code that runs on the board, and are committed.

## License

[MIT](LICENSE)
