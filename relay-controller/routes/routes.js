var MAX_RELAY = 8;

var appRouter = function (app) {

    app.get("/", function (req, res) {
        res.status(200).send("Relay Controller landing page goes here");
    });

    app.get("/relays", (req, res, next) => {
        res.json(["Fridge:ON", "Freezer:ON", "Rack:ON", "Master_Heater:ON", "Kurt_Heater:OFF", "Ronin_Heater:OFF"]);
    });

    app.get("/user", function (req, res) {
        var data = ({
            firstName: faker.name.firstName(),
            lastName: faker.name.lastName(),
            username: faker.internet.userName(),
            email: faker.internet.email()
        });
        res.status(200).send(data);
    });

    app.get("/relay/:id/:state", function (req, res) {
        var users = [];
        var id = req.params.id;
        var state = req.params.state;
        var readState = state;

        if (isFinite(id) && id > 0 && id < MAX_RELAY) {
            console.log("Relay ID:" + id);
            console.log("Relay Requested State:" + state);
            console.log("Relay New Read State:" + readState);
            res.status(200).send("Relay:" + id + ", state:" +readState);
        } else {
            res.status(400).send({ message: 'invalid Relay ID supplied' });
        }
    });

}

// write a function thats get the GPIO from the pin id supplied. 
// this information should be supplied in a config.json file
var getRelayStatus = function (id,state) {
    // get the GPIO for this id

    // get the state from the corresponding GPIO
}

var setRelayStatus = function (id,state) {
    // get the GPIO for this id

    // set the new GPIO to value from state

}

module.exports = appRouter;
