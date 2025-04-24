#include <FreeRTOS.h>
#include <task.h>
#include <Arduino.h>
#include <SoftwareSerial.h>
#include <Adafruit_NeoPixel.h>
#include "DHT.h"
#include "MQ135.h"
// define pins for uart LORA
#define RX 1
#define TX 0
SoftwareSerial myserial(RX, TX); // RX, TX
// define pins for neopixel
#define NEO_PIN   23
#define NUMPIXELS 1
Adafruit_NeoPixel pixels(NUMPIXELS, NEO_PIN, NEO_GRB + NEO_KHZ800);
uint8_t  brightness = 0;
// define pin inled
#define LED_PIN 25
// define pins for DHT22
#define dhtPIN 16
#define dhtTYPE DHT22
DHT dht(dhtPIN, dhtTYPE);
// define pins for MQ 135
#define MQ135_PIN 34
MQ135 gasSensor = MQ135(MQ135_PIN, 4095);
// Variables para almacenar temperatura, humedad, ambiente
float temperature = 0.0, humidity = 0.0;
int ppm = 0;
// Variables delay tareas
int ms_neo = 40, ms_ambient = 333, ms_temp_hum = 250;

void init_lora();
void lora(void *parameter);
void dht22(void *parameter);
void mq135(void *parameter);
void neopixel(void *parameter);
void send_ms(String ms);

void setup(){
    pixels.begin();
    pixels.show();
    pinMode(LED_PIN, OUTPUT);
    pinMode(MQ135_PIN, INPUT);
    dht.begin();
    myserial.begin(115200);
    Serial.begin(115200);
    init_lora();
    xTaskCreate(lora, "lora", 5000, NULL, 5, NULL);
    xTaskCreate(dht22, "dht22", 1000, NULL, 3, NULL);
    xTaskCreate(mq135, "mq135", 1000, NULL, 3, NULL);
    xTaskCreate(neopixel, "neopixel", 1000, NULL, 2, NULL);
}

void loop(){}

void init_lora() {
    Serial.println("\nConfigurando parametro antena LoRa\n");
    delay(2000);
    send_ms("AT"); // verificar estado de comandos
    delay(1000);
    send_ms("AT+ADDRESS=1"); // colocar direccion lora 0 - 65535
    delay(1000);
    send_ms("AT+NETWORKID=5"); // colocando direccion de red
    delay(1000);
    send_ms("AT+PARAMETER=9,7,1,12"); // RF parameters
    delay(1000);
    send_ms("AT+MODE?"); // operation mode
    delay(1000);
    send_ms("AT+CPIN?"); // contraseña
    delay(1000);
}
void send_ms(String ms) {
    myserial.println(ms); // mandar mensaje
    Serial.println(ms); // imprimir mensaje
    delay(500);
    while (myserial.available()) {
        Serial.print(char(myserial.read()));  // Si hay respuesta imprimirla en el monitor serial 
    }
}
void lora(void *parameter){
    while(1){
        String data = String(temperature) + "," + String(humidity) + "," + String(ppm);
        String datalen = String(data.length());
        Serial.println("Sending data: " + datalen + "," + data);
        send_ms("AT+SEND=2," + datalen + "," + data); // Enviar datos
        digitalWrite(LED_PIN, LOW);
        delay(3990);
        digitalWrite(LED_PIN, HIGH);
        delay(10);
    }
}
void dht22(void *parameter){
    while(1){
        humidity = dht.readHumidity();
        temperature = dht.readTemperature();
        delay(ms_temp_hum);
    }
}
void mq135(void *parameter){
    while(1){
        ppm = gasSensor.getPPM();
        delay(ms_ambient);
    }
}
void neopixel(void *parameter){
    bool increasing = true;
    while(1){
        if (increasing) {
            brightness += 4;
            if (brightness >= 200) {
                increasing = false;
            }
        } else {
            brightness -= 4;
            if (brightness <= 4) {
                increasing = true;
            }
        }
        pixels.setPixelColor(0, pixels.Color(0, 255, 255)); // led, rojo, verde, azul
        pixels.setBrightness(brightness);
        pixels.show();
        delay(ms_neo);
    }
}