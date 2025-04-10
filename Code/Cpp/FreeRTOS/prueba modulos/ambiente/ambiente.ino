#include <FreeRTOS.h>
#include <task.h>

#include "MQ135.h"

#define MQ135_PIN 16
MQ135 gasSensor = MQ135(MQ135_PIN, 4095);

void mq135(void *paramter);
void blink(void *parameter);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(MQ135_PIN, INPUT);
  // Create tasks
  xTaskCreate(mq135, "mq135", 300, nullptr, 2, nullptr);
  xTaskCreate(blink, "blink", 128, nullptr, 1, nullptr);
}

void loop() {}

void mq135(void *parameter) {
  (void)parameter; // Evitar advertencias de compilación
  while (1) {
    int ppm = gasSensor.getPPM();
    Serial.print("PPM: ");
    Serial.println(ppm);
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