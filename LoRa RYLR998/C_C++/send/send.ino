#include <SoftwareSerial.h>
#include "DHT.h"
#include <Adafruit_NeoPixel.h>

// Definir pines para UART
#define RX 1
#define TX 0

SoftwareSerial myserial(RX, TX); // RX, TX

#define LED_PIN 25
#define dhtPIN 14
#define dhtTYPE DHT22
DHT dht(dhtPIN, dhtTYPE);

#define PIN       23
#define NUMPIXELS 1
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

// Variables para almacenar temperatura y humedad
float temperature = 0.0, humidity = 0.0;

void send_ms(String ms) {
    myserial.println(ms); // mandar mensaje
    Serial.println(ms); // imprimir mensaje
    delay(500);
    while (myserial.available()) {
        Serial.print(char(myserial.read()));  // Si hay respuesta imprimirla en el monitor serial 
    }
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

void setup() {
    Serial.begin(115200);
    myserial.begin(115200);
    pinMode(LED_PIN, OUTPUT);
    delay(5000);
    dht.begin(); 
    // Inicializar LoRa
    init_lora();
    // Inicializar NeoPixel
    pixels.begin();
    pixels.show(); // Inicializar todos los píxeles a 'apagado'
}

void loop() {
    temperature = dht.readHumidity();
    humidity = dht.readTemperature();

    String data = String(temperature) + "," + String(humidity);
    String datalen = String(data.length());
    Serial.println("Sending data: " + data);
    send_ms("AT+SEND=2," + datalen + "," + data); // Enviar datos
    digitalWrite(LED_PIN, HIGH);
    delay(6000);
    digitalWrite(LED_PIN, LOW);
    delay(3000);

    // Encender NeoPixel con color azul estilo ultravioleta
    pixels.setPixelColor(0, pixels.Color(0, 0, 255)); // Azul
    pixels.show();
}