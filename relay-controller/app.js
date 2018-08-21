var express = require("express");
var bodyParser = require("body-parser");
var app = express();
var rpio = require('rpio');
var config = require('config');


var port = config.get('RelayController.serverConfig.port');
var pins = config.get('RelayController.relays.pins').split(",") ;
var states = config.get('RelayController.relays.bootState').split(",");

console.log("Server starting Port %d", port)

for( i=0; i< pins.length; i++){
	console.log("Relay %d assigned to pin %d as bootState: %d", i, pins[i],states[i]);
}

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

var routes = require("./routes/routes.js")(app);

var server = app.listen(port, function () {
    console.log("Listening on port %s...", server.address().port);
});

console.log("Setting relays to state as defined in config file. ");

for (i=0; i < pins.length; i++ ) {
	console.log( "Switching relay: %d to %d", pins[i], states[i] );
	rpio.open(pins[i], rpio.OUTPUT);
	rpio.write(pins[i], parseInt(states[i]) ); 
}

