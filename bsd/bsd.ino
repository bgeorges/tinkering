/**
   A small project at the request of my friend and colleague @ffeldmann
   This is an arduino sketch that runs on the Arduino Yun.
   This project shows a webpage where people can press the "BullShit" button which in turns will trigger an alarm and light some pixels

   BSDetector is a microservice accessible as a REST endpoint - seriously :)
   REST endpoints can be (GET) called over http as follow
   "http://${ARDUINO_IP}/arduino/bs/0"     -> set BS alarm off
   "http://${ARDUINO_IP}/arduino/bs/1"     -> set BS alarm on
   "http://${ARDUINO_IP}/arduino/health"   -> returns how many times one called bullshit, as JSON
   Every endpoint answers with {"bshits": <count>}.

   Copy config.example.h to config.h before compiling.

   @author Bruno P. Georges
*/

#include <Bridge.h>
#include <BridgeServer.h>
#include <BridgeClient.h>
#include <Adafruit_NeoPixel.h>
#include "config.h"

#ifdef __AVR__
#include <avr/power.h>
#endif

// The arduino will be listening to the  port 80 (and not 5555 when using YunServer class)
BridgeServer server;

uint16_t bshits = 0;  // bs counter, cater for enough
#define BOOT_PIN 12       // will flash when arduino init to show all will go well.
#define BS_PIN BOOT_PIN   // same LED, stays lit while BS is called

// Files on the Yun's SD card (/mnt/sd links to /mnt/sda1)
#define SD_ROOT "/mnt/sd"
#define WEB_PATH "/sd/bsdetector/"   // served from SD_ROOT/arduino/www/bsdetector/

// TONES
#define SPEAKER_PIN  9 // must be a PWM pin (digital 9, 10 or 11)
uint16_t tones[] = {261, 277, 294, 311, 330, 349, 370, 900, 1480, 2960}; // freq x * Hz

// NEOPIXELS
#define NEOPIXEL_PIN   6
#define NUMPIXELS      64 // 8x8 matrix; at full white that's ~3.8 A, size the supply accordingly
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

// The YUN IP Address. Value will be set from DHCP leased IP during setup()
String yunAddr;

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
  flashLed(BOOT_PIN, 2, 100);
  makeNoise(2, tones[9], 100);
  sendIP();
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
  command.trim(); // a command at the end of the URL can arrive with a trailing newline
  if (command == "bs") {
    int value = client.parseInt();
    digitalWrite(BS_PIN, value);
    if (value == 1) {
      ++bshits;
      // answer first: the reply is only sent once the connection closes,
      // and the alarm blocks for several seconds
      printJSonHealth(client);
      client.stop();
      bsAlarm();
      return;
    }
  }
  else if (command != "health") {
    client.print("{\"error\":\"unknown command\"}");
    return;
  }
  printJSonHealth(client);
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
void makeNoise(uint16_t reps, uint16_t freq, uint16_t d) {
  for (uint16_t i = 0; i < reps; i++) {
    tone(SPEAKER_PIN, freq);
    delay(d);
    noTone(SPEAKER_PIN);
    delay(d);
  }
  noTone(SPEAKER_PIN);
}

void printJSonHealth(BridgeClient client) {
  client.print("{\"bshits\":");
  client.print(bshits);
  client.print("}");
}

void bsAlarm() {
  makeNoise(144, tones[8], 20); // ~6 s; was "400", which a uint8_t silently cut to 144
  for (uint16_t i = 0; i < 70 ; i++) {
    lightUp(255, 0, 0, 50);
    ledOFF();
    delay(50);
  }
  ledOFF();
}

// r,g,b: color values ranging from 0,0,0 to 255,255,255
// d: how long to keep the pixels lit, in ms
void lightUp(uint8_t r, uint8_t g, uint8_t b, unsigned long d) {
  pixels.fill(pixels.Color(r, g, b));
  pixels.show(); // one update for the whole strip
  delay(d);
}

void ledOFF() {
  pixels.clear();
  pixels.show();
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

// Email the detector's URL to NOTIFY_EMAILS (see config.h) using ssmtp.
// SD_ROOT/mail_header.txt must hold the To/From/Subject header lines.
void sendIP() {
  String recipients = NOTIFY_EMAILS;
  if (recipients.length() == 0) {
    return;
  }
  Process p;
  String link = "http://" + yunAddr + WEB_PATH;
  p.runShellCommand("cat " SD_ROOT "/mail_header.txt > " SD_ROOT "/mail.txt");
  p.runShellCommand("echo \"" + link + "\" >> " SD_ROOT "/mail.txt");
  p.runShellCommand("cat " SD_ROOT "/mail.txt | ssmtp " + recipients);
}
