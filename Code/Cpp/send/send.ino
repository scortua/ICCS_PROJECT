#include <Arduino.h>
#include <SoftwareSerial.h>
#include <Adafruit_NeoPixel.h>
#include "DHT.h"

// define pins for uart LORA
#define RX 1
#define TX 0
SoftwareSerial myserial(RX, TX); // RX, TX
// define pins for DHT22
#define LED_PIN 25
#define dhtPIN 14
#define dhtTYPE DHT22
DHT dht(dhtPIN, dhtTYPE);
// define pins for NeoPixel
#define NEO_PIN   23
#define NUMPIXELS 1
Adafruit_NeoPixel pixels(NUMPIXELS, NEO_PIN, NEO_GRB + NEO_KHZ800);
uint8_t  brightness = 180; 
// define pins for MQ 135
#define MQ135_PIN 34
// Variables para almacenar temperatura y humedad
float temperature = 0.0, humidity = 0.0;

void init_lora();
void send_ms(String ms);

void setup() {
    Serial.begin(115200);
    myserial.begin(115200);
    pinMode(LED_PIN, OUTPUT);
    delay(2500);
    // Inicializar DHT
    dht.begin(); 
    // Inicializar LoRa
    init_lora();
    // Inicializar led indicador
    pwm(5,100,100); // Configurar PWM en el pin LED_PIN a 1000 Hz
    // Inicializar MQ135
    pinMode(MQ135_PIN, INPUT);
    // Inicializar NeoPixel
    pixels.begin();
    pixels.setPixelColor(0, pixels.Color(0, 255, 255)); // led, rojo, verde, azul
    pixels.setBrightness(brightness);
    pixels.show();
}

void loop() {
    humidity = dht.readHumidity();
    temperature = dht.readTemperature();
    ambiente = analogRead(MQ135_PIN);
    String data = String(temperature) + "," + String(humidity) + "," + String(ambiente);
    String datalen = String(data.length());
    Serial.println("Sending data: " + datalen + "," + data);
    send_ms("AT+SEND=2," + datalen + "," + data); // Enviar datos
    digitalWrite(LED_PIN, HIGH);
    delay(3500);
    digitalWrite(LED_PIN, LOW);
    delay(500);
}

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