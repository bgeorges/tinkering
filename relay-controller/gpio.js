// Thin wrapper around rpio that speaks relay states ("ON"/"OFF") instead of
// pin levels, and keeps every relay pin in OUTPUT mode for its whole life.
//
// Set RELAY_MOCK=1 to run without a Raspberry Pi (pin levels kept in memory).

const MOCK = process.env.RELAY_MOCK === '1';

function mockRpio() {
    const levels = {};
    return {
        HIGH: 1,
        LOW: 0,
        OUTPUT: 1,
        open: (pin, mode, init) => { levels[pin] = init === undefined ? 0 : init; },
        read: (pin) => levels[pin] || 0,
        write: (pin, value) => { levels[pin] = value; }
    };
}

const rpio = MOCK ? mockRpio() : require('rpio');

const STATES = ['ON', 'OFF'];

let activeLow = true;

function levelFor(state) {
    const on = state === 'ON';
    return (on === activeLow) ? rpio.LOW : rpio.HIGH;
}

// Normalise user input ("on", "Off", ...) to "ON"/"OFF", or null if invalid.
function parseState(value) {
    const state = String(value).toUpperCase();
    return STATES.includes(state) ? state : null;
}

// Open every relay pin as an output, driven straight to its boot state so the
// relay never flickers through the opposite state.
function setup(relays, isActiveLow) {
    activeLow = isActiveLow;
    relays.forEach((relay) => {
        rpio.open(relay.pin, rpio.OUTPUT, levelFor(relay.bootState));
    });
}

// Reading an output pin returns the level it is driving; the pin mode is not
// touched, so reading never switches the relay.
function getState(pin) {
    const level = rpio.read(pin);
    return level === levelFor('ON') ? 'ON' : 'OFF';
}

function setState(pin, state) {
    rpio.write(pin, levelFor(state));
}

module.exports = { MOCK, parseState, setup, getState, setState };
