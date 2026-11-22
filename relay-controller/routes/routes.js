const crypto = require('crypto');
const express = require('express');
const gpio = require('../gpio');

// relays: [{ id, name, pin, bootState }] from config
// apiKey: shared secret every /relay* and /config request must send in X-API-Key
module.exports = function (app, { relays, apiKey, publicConfig }) {
    const expectedKey = Buffer.from(apiKey);

    function requireApiKey(req, res, next) {
        const given = Buffer.from(req.get('X-API-Key') || '');
        if (given.length === expectedKey.length && crypto.timingSafeEqual(given, expectedKey)) {
            return next();
        }
        res.status(401).json({ message: 'missing or invalid X-API-Key header' });
    }

    function findRelay(id) {
        return relays.find((relay) => String(relay.id) === String(id));
    }

    function describe(relay) {
        return { id: relay.id, name: relay.name, pin: relay.pin, state: gpio.getState(relay.pin) };
    }

    app.get('/', (req, res) => {
        res.send('Relay Controller. See README for the API.');
    });

    const api = express.Router();
    api.use(requireApiKey);

    api.get('/config', (req, res) => {
        res.json(publicConfig);
    });

    api.get('/relays', (req, res) => {
        res.json(relays.map(describe));
    });

    api.put('/relays/:state', (req, res) => {
        const state = gpio.parseState(req.params.state);
        if (!state) {
            return res.status(400).json({ message: 'state must be ON or OFF' });
        }
        relays.forEach((relay) => {
            console.log('Switching %s relay %d (%s) on pin %d', state, relay.id, relay.name, relay.pin);
            gpio.setState(relay.pin, state);
        });
        res.json(relays.map(describe));
    });

    api.get('/relay/:id', (req, res) => {
        const relay = findRelay(req.params.id);
        if (!relay) {
            return res.status(404).json({ message: 'unknown relay ' + req.params.id });
        }
        res.json(describe(relay));
    });

    api.put('/relay/:id/:state', (req, res) => {
        const relay = findRelay(req.params.id);
        if (!relay) {
            return res.status(404).json({ message: 'unknown relay ' + req.params.id });
        }
        const state = gpio.parseState(req.params.state);
        if (!state) {
            return res.status(400).json({ message: 'state must be ON or OFF' });
        }
        console.log('Switching %s relay %d (%s) on pin %d', state, relay.id, relay.name, relay.pin);
        gpio.setState(relay.pin, state);
        res.json(describe(relay));
    });

    // Switching used to be a GET. Point old clients at PUT instead of a bare 404.
    api.get(['/relays/:state', '/relay/:id/:state'], (req, res) => {
        res.status(405).set('Allow', 'PUT').json({ message: 'use PUT to switch relays' });
    });

    app.use(api);
};
