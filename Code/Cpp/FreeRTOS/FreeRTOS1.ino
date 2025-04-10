#include <freeRTOS.h>
#include <task.h>
#include <Arduino.h>
#include <SoftwareSerial.h>
// define libaries for diferent devices
#include <Adafruit_NeoPixel.h>
#include "DHT.h"
#include "MQ135.h"
// defien pins for uart LORA
#define RX 1
#define TX 0
SoftwareSerial myserial(RX, TX); // RX, TX
// define pins for DHT22
#define dhtPIN 16
#define dhtTYPE DHT22
DHT dht(dhtPIN, dhtTYPE);
// define pins for MQ 135
#define MQ135_PIN 34
MQ135 gasSensor = MQ135(MQ135_PIN, 4095);
// define pins for neopixel
#define NEO_PIN   23
#define NUMPIXELS 1
Adafruit_NeoPixel pixels(NUMPIXELS, NEO_PIN, NEO_GRB + NEO_KHZ800);
uint8_t  brightness = 0;
// variables for temperature, humidity, ambient
float temperature = 0.0, humidity = 0.0;
int ppm = 0;
// variables delay tasks
int ms_neo = 40, ms_ambient = 333, ms_temp_hum = 250;

void init_lora();
void lora(void *parameter);     // define pin for LORA
void dht22(void *parameter);    // define pin for DHT22
void mq135(void *parameter);    // define pin for MQ135
void dirt(void *parameter);     // define pin for dirt
void neopixel(void *parameter); // define pin for neopixel
void pump(void *parameter);     // define pin for pump
void send_ms(String ms);        // send message to LORA

void setup(){

}

void loop(){}

void init_lora(){

}

void send_ms(){

}

void lora(){

}

void dht22(){

}

void mq135(){

}

void dirt(){

}

void neopixel(){

}

void pump(){

}