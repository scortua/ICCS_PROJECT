#include <FreeRTOS.h>
#include <task.h>

#include "DHT.h"

#define DHTPIN 14
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

void temp_hum(void *parameter);
void blink(void *parameter);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  dht.begin();
  // Create tasks
  xTaskCreate(temp_hum, "dht22", 300, nullptr, 2, nullptr);
  xTaskCreate(blink, "blink", 128, nullptr, 1, nullptr);
}

void loop() {}

void temp_hum(void *parameter) {
  (void)parameter; // Evitar advertencias de compilación
  while (1) {
    float h = dht.readHumidity();
    float t = dht.readTemperature();
    if (isnan(h) || isnan(t)) {
      Serial.println("Error al leer el sensor DHT22");
    }
    Serial.print("Humedad: ");
    Serial.print(h);
    Serial.print("%  Temperatura: ");
    Serial.print(t);
    Serial.println("°C");
    vTaskDelay(2000 / portTICK_PERIOD_MS); // Esperar 2 segundos
  }
}
void blink(void *parameter) {
  (void)parameter; // Evitar advertencias de compilación
  while (1) {
    digitalWrite(LED_BUILTIN, HIGH); // Enciende el LED
    vTaskDelay(500 / portTICK_PERIOD_MS); // Espera 500 ms
    digitalWrite(LED_BUILTIN, LOW); // Apaga el LED
    vTaskDelay(500 / portTICK_PERIOD_MS); // Espera 500 ms
  }
}