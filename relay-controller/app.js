const express = require('express');
const config = require('config');
const gpio = require('./gpio');

const serverConfig = config.get('RelayController.serverConfig');
const relayConfig = config.get('RelayController.relays');

const apiKey = process.env.RELAY_API_KEY;
if (!apiKey) {
    console.error('RELAY_API_KEY is not set. Refusing to start an unauthenticated relay API.');
    process.exit(1);
}

const relays = relayConfig.list.map((relay) => {
    const bootState = gpio.parseState(relay.bootState);
    if (!bootState) {
        console.error('Relay %s: bootState must be ON or OFF, got %j', relay.id, relay.bootState);
        process.exit(1);
    }
    return { id: relay.id, name: relay.name, pin: relay.pin, bootState };
});

if (gpio.MOCK) {
    console.log('RELAY_MOCK=1: GPIO is simulated, no pins will be driven.');
}

console.log('Setting relays to their boot state (active %s).', relayConfig.activeLow ? 'low' : 'high');
gpio.setup(relays, relayConfig.activeLow);
relays.forEach((relay) => {
    console.log('Relay %d (%s) on pin %d: %s', relay.id, relay.name, relay.pin, relay.bootState);
});

const app = express();
require('./routes/routes.js')(app, {
    relays,
    apiKey,
    publicConfig: config.util.toObject(config.get('RelayController'))
});

const server = app.listen(serverConfig.port, serverConfig.host, () => {
    const address = server.address();
    console.log('Listening on %s:%d', address.address, address.port);
});
