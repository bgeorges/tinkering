var fs = require("fs");
var rpio = require('rpio');

var MAX_RELAY = 8;

// map pysical pins to relays, in the order of the array.
var gpioPins = [29,33,35,37]

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

    app.get("/relays/:state", (req, res, next) => {
        var state = req.params.state;
        if (state == 'ON') {
		for (i=0; i < gpioPins.length; i++ ) {
	           console.log( "Switching ON relay:" + i + " on pin: "+ gpioPins[i] );
	    	   rpio.open(gpioPins[i], rpio.OUTPUT);
	    	   rpio.write(gpioPins[i], rpio.LOW) // yeah I know, will submit a PR for this at some point.
		}

	} else if  (state == 'OFF') {
		for (i=0; i < gpioPins.length; i++ ) {
	           console.log( "Switching OFF relay:" + i + " on pin: "+ gpioPins[i] + "\n" );
	    	   rpio.open(gpioPins[i], rpio.OUTPUT);
	    	   rpio.write(gpioPins[i], rpio.HIGH)
		}
	} else {
		res.status(400).send({ message: 'invalid State supplied' });
	}
	res.json("All relays are now: "+state);
    });

    app.get("/relay/:id", (req, res, next) => {
        var id = req.params.id;
	i = id -1
        if (isFinite(id) && i<gpioPins.length) {
	    var pin = gpioPins[i]
	    rpio.open(pin, rpio.INPUT);
	    var pinState = rpio.read(pin)
	    console.log( "Relay:" + id + " is: " + pinState );
            res.json({ relay: id, state: pinState })
        }else{
	    console.log("Error reading relay:"+ id+ " on pin: "+ pin);
	    res.json("Error reading relay:"+ id+ " on pin: "+ pin);
	}
    });

    app.get("/relay/:id/:state", function (req, res) {
        var id = req.params.id;
        var state = req.params.state;
        var readState = state;
        console.log("Relay ID:" + id);
        console.log("Request to turn relay "+id+" " + state );
	i = id -1;

        if (isFinite(i) && (state == 'ON'|| state == "OFF") && i<gpioPins.length ) {
	    var pin = gpioPins[i];
	    rpio.open(pin, rpio.OUTPUT, rpio.HIGH);
	    if ( state == 'ON'){
        	console.log("Turning ON Relay: " + id );
	    	rpio.write(pin, rpio.LOW)
	    }else{
 	    	console.log("Turning OFF Relay: " + id );
	    }
            res.json({ relay: id, state: readState })
        } else {
            console.log("Invalid Relay number and/or State supplied");
            res.status(400).send({ message: 'invalid Relay number and/or State supplied' });
        }
    });

}

module.exports = appRouter;
