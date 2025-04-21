#include <FreeRTOS.h>
#include <task.h>
#include <Arduino.h>
#include <SoftwareSerial.h>
// define libaries for diferent devices
#include <Adafruit_NeoPixel.h>
#include "DHT.h"
#include "MQ135.h"
#include <WiFi.h>
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
// define wifi
#ifndef STASSID
#define STASSID "SSID"
#define STAPSK "PASSWORD"
#endif

const char* SSID = STASSID;
const char* PASSWORD = STAPSK;
// variables for temperature, humidity, ambient
float temperature = 0.0, humidity = 0.0;
int ppm = 0, ambiente = 0;
String data, datalen;
// variables delay tasks
int ms_neo = 40, ms_ambient = 333, ms_temp_hum = 250, ms_wifi = 150000;

void init_lora();
void lora(void *parameter);     // define pin for LORA
void dht22(void *parameter);    // define pin for DHT22
void mq135(void *parameter);    // define pin for MQ135
void dirt(void *parameter);     // define pin for dirt
void neopixel(void *parameter); // define pin for neopixel
void pump(void *parameter);     // define pin for pump
void send_ms(String);        // send message to LORA
void wifitask(void *parameter); // define pin for wifi

void setup(){
    Serial.begin(115200);
    myserial.begin(115200); // LORA
    dht.begin();           // DHT22
    pixels.begin();      // neopixel
    pixels.show();
    init_lora(); // initialize LORA
    // create tasks
    xTaskCreate(lora, "lora", 10000, NULL, 4, NULL);
    xTaskCreate(dht22, "dht22", 10000, NULL, 1, NULL);
    xTaskCreate(mq135, "mq135", 10000, NULL, 1, NULL);
    xTaskCreate(dirt, "dirt", 10000, NULL, 1, NULL);
    xTaskCreate(neopixel, "neopixel", 10000, NULL, 1, NULL);
    xTaskCreate(pump, "pump", 10000, NULL, 3, NULL);
    xTaskCreate(wifitask, "wifi", 10000, NULL, 2, NULL);
}

void loop(){}

void init_lora(){
    delay(1000);
    Serial.println("\nConfigurando parametro antena LoRa\n");
    delay(1000);
    send_ms("AT"); // verificar estado de comandos
    delay(200);
    send_ms("AT+ADDRESS=1"); // colocar direccion lora 0 - 65535
    delay(200);
    send_ms("AT+NETWORKID=5"); // colocando direccion de red
    delay(200);
    send_ms("AT+PARAMETER=9,7,1,12"); // RF parameters
    delay(200);
    send_ms("AT+MODE?"); // operation mode
    delay(200);
    send_ms("AT+CPIN?"); // contraseña
    delay(200);
}

void send_ms(String msg){
    myserial.println(msg); // mandar mensaje
    Serial.println(msg); // imprimir mensaje
    delay(500);
    while (myserial.available()) {
        Serial.print(char(myserial.read()));  // Si hay respuesta imprimirla en el monitor serial 
    }
}

void lora(void *parameter){
    (void)parameter; // Evitar advertencias de compilación
    while (1){
        data = String(temperature) + "," + String(humidity) + "," + String(ppm) + "," + String(ambiente);
        datalen = String(data.length());
        Serial.println("Sending data: " + datalen + "," + data);
        send_ms("AT+SEND=2," + datalen + "," + data); // Enviar datos
        vTaskDelay(180000 / portTICK_PERIOD_MS); // Esperar 3 min
    }
}

void dht22(void *parameter){
    (void)parameter; // Evitar advertencias de compilación
    while (1){
        humidity = dht.readHumidity(); // leer humedad
        temperature = dht.readTemperature(); // leer temperatura
        if (isnan(humidity) || isnan(temperature)) {
            Serial.println("Error al leer el sensor DHT22");
            return;
        }
        Serial.print("Humedad: ");
        Serial.print(humidity);
        Serial.print("%  Temperatura: ");
        Serial.print(temperature);
        Serial.println("°C");
        vTaskDelay(ms_temp_hum / portTICK_PERIOD_MS); // Esperar 250 ms
    }
}

void mq135(void *parameter){
    (void)parameter; // Evitar advertencias de compilación
    while (1){
        ppm = gasSensor.getPPM(); // leer ppm
        Serial.print("PPM: ");
        Serial.println(ppm);
        vTaskDelay(ms_ambient / portTICK_PERIOD_MS); // Esperar 333 ms
    }
}

void dirt(void *parameter){
    (void)parameter; // Evitar advertencias de compilación
    while (1){
        ambiente = analogRead(MQ135_PIN); // leer dirt
        Serial.print("Dirt: ");
        Serial.println(ambiente);
        vTaskDelay(ms_ambient / portTICK_PERIOD_MS); // Esperar 333 ms
    }
}

void neopixel(void *parameter){
    (void)parameter; // Evitar advertencias de compilación
    while (1){
        Serial.println("luces" );
    }
}

void pump(void *parameter){
    (void)parameter; // Evitar advertencias de compilación
    while (1){
        digitalWrite(LED_BUILTIN, HIGH); // Enciende el LED
        vTaskDelay(333 / portTICK_PERIOD_MS); // Espera 500 ms
        digitalWrite(LED_BUILTIN, LOW); // Apaga el LED
        vTaskDelay(333 / portTICK_PERIOD_MS); // Espera 500 ms
    }
}

void wifitask(void *parameter){
    (void)parameter; // Evitar advertencias de compilación
    WiFi.begin(SSID, PASSWORD); // Conectar a WiFi
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
    }
    while (1){
        Serial.println("Conectado a WiFi...");
        Serial.println("IP Address: " + WiFi.localIP().toString());
        Serial.println("Signal Strength: " + String(WiFi.RSSI()) + " dBm");
        Serial.println("MAC Address: " + WiFi.macAddress() + "\n");
        vTaskDelay(ms_wifi / portTICK_PERIOD_MS); // Esperar 5 segundos
    }
}