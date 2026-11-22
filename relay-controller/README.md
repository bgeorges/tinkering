# Remote Relay Controller

REST API to switch relays wired to a Raspberry Pi's GPIO pins.

## Install
Requires Node.js 18 or later.

```bash
npm install
```

## Run
The API refuses to start without a shared key. Every request except `/` must send it in the `X-API-Key` header.

```bash
export RELAY_API_KEY="$(openssl rand -hex 32)"
npm start
```

To try the API on a machine without GPIO (pin levels are simulated in memory):

```bash
RELAY_API_KEY=dev npm run mock
```

## Configure
Edit [`config/default.json`](config/default.json):

| Key | Meaning |
|---|---|
| `serverConfig.host` | Interface to listen on. `0.0.0.0` = whole network, `127.0.0.1` = this Pi only. |
| `serverConfig.port` | HTTP port (default `8080`). |
| `relays.activeLow` | `true` if a LOW pin turns the relay ON (most cheap relay boards). |
| `relays.list[]` | One entry per relay: `id`, `name`, physical `pin` number, and `bootState` (`ON`/`OFF`) applied at startup. |

## Use
Reading a relay never changes it. Switching uses `PUT`.

### List all relays and their state
```bash
curl -H "X-API-Key: $RELAY_API_KEY" http://localhost:8080/relays
```

### Get state of relay 1
```bash
curl -H "X-API-Key: $RELAY_API_KEY" http://localhost:8080/relay/1
```

### Switch OFF relay 3
```bash
curl -X PUT -H "X-API-Key: $RELAY_API_KEY" http://localhost:8080/relay/3/OFF
```

### Switch ON all relays
```bash
curl -X PUT -H "X-API-Key: $RELAY_API_KEY" http://localhost:8080/relays/ON
```

### Show the running config
```bash
curl -H "X-API-Key: $RELAY_API_KEY" http://localhost:8080/config
```

Responses are JSON: `{ "id": 3, "name": "room1_Heater", "pin": 35, "state": "OFF" }`.

### Upgrading from 1.x
- Switching moved from `GET` to `PUT`. Old `GET /relay/:id/:state` calls now get `405`.
- `RELAY_API_KEY` is required.
- `bootState` is now `ON`/`OFF` per relay instead of raw pin levels; the shipped config keeps the old boot behaviour.

## Pin mapping
Pins in the config are physical header numbers.

| Relay | Physical | BCM |
|---|---|---|
| 1 | 29 | 5 |
| 2 | 33 | 13 |
| 3 | 35 | 19 |
| 4 | 37 | 26 |
