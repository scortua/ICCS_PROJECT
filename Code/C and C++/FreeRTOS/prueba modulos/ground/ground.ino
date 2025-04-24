#include <FreeRTOS.h>
#include <task.h>

#define sensor_pin 26

void tierra(void *parameter);
void blink(void *parameter);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  analogReadResolution(12); // Configurar resolución de lectura analógica
  // Create tasks
  xTaskCreate(tierra, "ground", 300, nullptr, 2, nullptr);
  xTaskCreate(blink, "blink", 128, nullptr, 1, nullptr);
}

void loop() {}

void tierra(void *parameter) {
  (void)parameter; // Evitar advertencias de compilación
  while (1) {
    int sensorValue = analogRead(sensor_pin);
    Serial.print("Valor del sensor: ");
    Serial.println(sensorValue);
    Serial.print("Voltaje: ");
    Serial.print(sensorValue * (3.3 / 4095.0)); // Convertir a voltaje
    Serial.println("V");
    vTaskDelay(500 / portTICK_PERIOD_MS); // Esperar 2 segundos
  }
}
void blink(void *parameter) {
  (void)parameter; // Evitar advertencias de compilación
  while (1) {
    digitalWrite(LED_BUILTIN, HIGH); // Enciende el LED
    vTaskDelay(333 / portTICK_PERIOD_MS); // Espera 500 ms
    digitalWrite(LED_BUILTIN, LOW); // Apaga el LED
    vTaskDelay(333 / portTICK_PERIOD_MS); // Espera 500 ms
  }
}