/**
 * A small project at the request of my friedn and colleague @ffeldmann
 * This is an arduino sketch that runs on the Arduino Yun.
 * This project shows a webpage where people can press the "BullShit" button which in turns will trigger an alarm and light some pixels
 * 
 * BSDetector is a microservice accessible as a REST endpoint - seriously :)
 * REST endpoints can be (GET) called over http as follow
 * "http://${ARDUINO_IP}/arduino/bs/0"     -> set BS allarm off
 * "http://${ARDUINO_IP}/arduino/bs/1"     -> set BS allarm on
 * "http://${ARDUINO_IP}/arduino/health"   -> returns info on how many times one calls bullshit, plus other thinks
 * 
 * @author Bruno P. Georges
 */

#include <Bridge.h>
#include <BridgeServer.h>
#include <BridgeClient.h>
#include <Adafruit_NeoPixel.h>

#ifdef __AVR__
#include <avr/power.h>
#endif

// The arduino will be listening to the  port 80 (and not 5555 when using YunServer class)
BridgeServer server;

uint16_t bshits = 0;  // bs counter, cater for enough
#define BS_PIN 12     // will lite when BS is called
#define BOOT_PIN 12   // will flash when arduino init to show all will go well.

// TONES
#define SPEAKER_PIN  9 // must be a PWM pin (digital 9, 10 or 11)
uint8_t tones[] = {261, 277, 294, 311, 330, 349, 370, 392, 415, 840}; // freq x * Hz

// NEOPIXELS
#define NEOPIXEL_PIN   6
#define NUMPIXELS      64 // for now, we are panning 16x8, that's almost 8 Amp !
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

// The YUN IP Address. Value will be set from DHCP leased IP during setup()
String yunAddr;
// the url to access the Yun REST enpoints 
String bsURL; // 

// no serial, using BOOT_PIN to show things are going as planned.
void setup() {
  pinMode(SPEAKER_PIN, OUTPUT);
  pinMode(BOOT_PIN, OUTPUT);
  pixels.begin();
  Bridge.begin();
  flashLed(BOOT_PIN, 3, 300);
  server.listenOnLocalhost();
  server.begin();
  yunAddr = getIPaddr();
  bsURL = "http://" + yunAddr + "/arduino/";
  // set the ipaddr value with the one we got from DHCP
  flashLed(BOOT_PIN, 2, 100);
  makeNoise(2, tones[1], 100);
  ledOFF();
}


void loop() {
  BridgeClient client = server.accept();
  if (client) {
    process(client);
    client.stop();
  }
  delay(50);
}

void process(BridgeClient client) {
  // read the command
  String command = client.readStringUntil('/');
  printHtmlPage(client);
  if (command == "bs") {
    int value = 0;
    value = client.parseInt();
    digitalWrite(BS_PIN, value);
    if (value == 1) {
      ++bshits;
      bsAlarm();
    }
  }
  else if ( command == "health") {
    printJSonHealth(client);
  }
}

void flashLed(uint8_t fpin, uint8_t times, uint16_t interval) {
  for (uint8_t i = 0; i < times; i++) {
    digitalWrite(fpin, HIGH);
    delay(interval);
    digitalWrite(fpin, LOW);
    delay(interval);
  }
}

// set the buzzer
// reps: how many times we send call tone()
// freq: value of the frequecy
// d: pause between tones in millis
void makeNoise(uint8_t reps, uint8_t freq, uint16_t d) {
  for (uint16_t i = 0; i < reps; i++) {
    tone(SPEAKER_PIN, freq);
    delay(d);
    noTone(SPEAKER_PIN);
    delay(d);
  }
  noTone(SPEAKER_PIN);
}

// remindes me the old days when we had to write our own c||perl CGI libs :)
void printHtmlPage(BridgeClient client) {
  client.println("Status: 200");
  client.println("Content-type: text/html");
  client.println();
  client.println("<html><head/><body><h2><b>");
  client.println("<a href='" + bsURL + "bs/1'>");
  client.println("<img src='/sd/bsdetector/bsButton.jpg' alt='BullShit!' width='60' height='60' border='0'/></a><br>");
  client.println("<a href='" + bsURL + "bs/0'>OFF</a></b> [admin only]<br>");
  client.println("</body></html>");
}

void printJSonHealth(BridgeClient client) {
  // print health stats in json format
  client.print("bshits:");
  client.print(bshits);
}

void bsAlarm() {
  makeNoise(30, tones[9], 5);
  for (uint16_t i = 0; i < 10 ; i++) {
    lightUp(255, 0, 0, 50);
    makeNoise(10, tones[9], 5);
    ledOFF();
    delay(50);
  }
  ledOFF();
}


// r,g,b: color values ranging from 0,0,0 to 255,255,255
// d: interval in ms
void lightUp(int r, int g, int b, long d) {
  for (uint16_t i = 0; i < pixels.numPixels(); i++) {
    pixels.setPixelColor(i, pixels.Color(r, g, b));
    pixels.show(); // This sends the updated pixel color to the hardware.
  }
}

// Fill the dots one after the other with no color
void ledOFF() {
  for (uint16_t i = 0; i < pixels.numPixels(); i++) {
    pixels.setPixelColor(i, 0);
    pixels.show();
  }
}


String getIPaddr(){
  String ipaddr;
  Process networkCheck;  // initialize a new process
  networkCheck.runShellCommand("ifconfig br-wan | awk '/inet addr/ {gsub(\"addr:\", \"\", $2); print $2}' ");
  while (networkCheck.available() > 0) {
    char c = networkCheck.read();
    ipaddr += c;
  }
  return ipaddr;
}
