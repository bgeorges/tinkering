var fs = require("fs");
var rpio = require('rpio');

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
        if (isFinite(id) && id > 0) {
	    console.log( "Reading Pin:" + id + "\n" );
	    rpio.open(id, rpio.INPUT);
	    var pinState =(rpio.read(id) ? 'high' : 'low');
	    console.log( "Pin:" + id + " is: " + pinState + "\n" );
            res.json({ id: id, state: pinState })
        }
    });

    app.get("/relay/:id/:state", function (req, res) {
        var id = req.params.id;
        var state = req.params.state;
        var readState = state;
        console.log("Relay ID:" + id);
        console.log("Relay Requested State:" + state);

        if (isFinite(id) && (state == 'ON'|| state == "OFF") ) {
	    rpio.open(id, rpio.OUTPUT, rpio.LOW);
	    if ( state == 'ON'){
        	console.log("Turning ON Relay ID:" + id );
	    	rpio.write(id, rpio.HIGH)
	    }else{
 	    	console.log("Turning OFF Relay ID:" + id );
	    }
            res.json({ id: id, state: readState })
        } else {
            res.status(400).send({ message: 'invalid Relay ID and State supplied' });
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
