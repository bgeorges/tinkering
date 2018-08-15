var MAX_RELAY = 8;

var appRouter = function (app) {

    app.get("/", function (req, res) {
        res.status(200).send("Relay Controller landing page goes here");
    });

    app.get("/relays", (req, res, next) => {
        res.json([
            { name: 'Fridge', id: '1', readState: 'ON' },
            { name: 'master_Heater', id: '2', readState: 'ON' },
            { name: 'room1_Heater', id: '3', readState: 'ON' },
            { name: 'room2_Heater', id: '4', readState: 'ON' }
        ]);
    });

    app.get("/relay/:id", (req, res, next) => {
        var id = req.params.id;
        if (isFinite(id) && id > 0 && id < MAX_RELAY) {
            res.json({ id: id, state: 'ON' })
        }
  
    });

    app.get("/relay/:id/:state", function (req, res) {
        var id = req.params.id;
        var state = req.params.state;
        var readState = state;
        //{state > 0) ? "ON" : "OFF";

        if (isFinite(id) && id > 0 && id < MAX_RELAY) {
            console.log("Relay ID:" + id);
            console.log("Relay Requested State:" + state);
            console.log("Relay New Read State:" + readState);
            res.json({ id: id, state: readState })
        } else {
            res.status(400).send({ message: 'invalid Relay ID supplied' });
        }
    });

}

// TODO
// write a function thats get the GPIO from the pin id supplied. 
// this information should be supplied in a config.json file
var getRelayStatus = function (id, state) {
    // get the GPIO for this id

    // get the state from the corresponding GPIO
}

// TODO
var setRelayStatus = function (id, state) {
    // get the GPIO for this id

    // set the new GPIO to value from state

}

module.exports = appRouter;
