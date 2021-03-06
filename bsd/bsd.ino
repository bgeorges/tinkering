/**
   A small project at the request of my friedn and colleague @ffeldmann
   This is an arduino sketch that runs on the Arduino Yun.
   This project shows a webpage where people can press the "BullShit" button which in turns will trigger an alarm and light some pixels

   BSDetector is a microservice accessible as a REST endpoint - seriously :)
   REST endpoints can be (GET) called over http as follow
   "http://${ARDUINO_IP}/arduino/bs/0"     -> set BS allarm off
   "http://${ARDUINO_IP}/arduino/bs/1"     -> set BS allarm on
   "http://${ARDUINO_IP}/arduino/health"   -> returns info on how many times one calls bullshit, plus other thinks

   @author Bruno P. Georges
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
#define ADMIN_EMAIL "bruno.georges@gmail.com"

// TONES
#define SPEAKER_PIN  9 // must be a PWM pin (digital 9, 10 or 11)
uint16_t tones[] = {261, 277, 294, 311, 330, 349, 370, 900, 1480, 2960}; // freq x * Hz

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
  SerialUSB.begin(9600);
  delay(1000);
  SerialUSB.println("Serial USB Open");
  pinMode(SPEAKER_PIN, OUTPUT);
  pinMode(BOOT_PIN, OUTPUT);
  pixels.begin();
  Bridge.begin();
  flashLed(BOOT_PIN, 3, 300);
  server.listenOnLocalhost();
  server.begin();
  delay(2000); // wait for all processes to start
  yunAddr = getIPaddr();
  bsURL = "http://" + yunAddr + "/arduino/";
  flashLed(BOOT_PIN, 2, 100);
  makeNoise(2, tones[9], 100);
  sendIP();
  buildStartPage();
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
void makeNoise(uint8_t reps, uint16_t freq, uint16_t d) {
  for (uint16_t i = 0; i < reps; i++) {
    tone(SPEAKER_PIN, freq);
    delay(d);
    noTone(SPEAKER_PIN);
    delay(d);
  }
  noTone(SPEAKER_PIN);
}

void printJSonHealth(BridgeClient client) {
  // print health stats in json format
  client.print("bshits:");
  client.print(bshits);
}

void bsAlarm() {
  makeNoise(400, tones[8], 20);
  for (uint16_t i = 0; i < 70 ; i++) {
    lightUp(255, 0, 0, 50);
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

String getIPaddr() {
  String ipaddr;
  Process networkCheck;  // initialize a new process
  networkCheck.runShellCommand("ifconfig br-wan | awk '/inet addr/ {gsub(\"addr:\", \"\", $2); print $2}' ");
  while (networkCheck.available() > 0) {
    char c = networkCheck.read();
    if (c != '\n') { // don't need the terminating "\n"
      ipaddr += c;
    }
  }
  return ipaddr;
}
 
void sendIP() {
  Process p;
  String link = "http://" + yunAddr + "/sd/bsdetector/";
  p.runShellCommand("cat /mnt/sd/mail_header.txt > /mnt/sd/mail.txt");
  p.runShellCommand("echo \"" + link + "\" >>  /mnt/sd/mail.txt");
  p.runShellCommand("cat /mnt/sd/mail.txt | ssmtp bruno.georges@gmail.com ffeldman@redhat.com "); //
}

void buildStartPage() {
  Process p;
  p.runShellCommand("cat /mnt/sda1/arduino/www/bsdetector/index.html.tmpl > /mnt/sda1/arduino/www/bsdetector/index.html");
  p.runShellCommand("sed -i \'s/ip_addr/"+yunAddr+"/g\' /mnt/sda1/arduino/www/bsdetector/index.html");
}


