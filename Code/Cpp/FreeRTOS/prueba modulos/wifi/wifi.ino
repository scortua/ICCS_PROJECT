#include <FreeRTOS.h>
#include <task.h>

#include <WiFi.h>

#ifndef STASSID
#define STASSID "ssid"
#define STAPSK "password"
#endif

const char* SSID = STASSID;
const char* PASSWORD = STAPSK;

void wifiTask(void *parameter);
void ledTask(void *parameter);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  // Create a task
  xTaskCreate(wifiTask, "WiFi Task", 10000, nullptr, 2, nullptr);
  xTaskCreate(ledTask, "LED Task", 128, nullptr, 1, nullptr);
}

void loop() {}

void wifiTask(void *parameter) {
  // put your main code here, to run repeatedly:
  WiFi.begin(SSID, PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
  }
  while (true) {
    Serial.println("Connecting to WiFi...");
    Serial.println("IP Address: " + WiFi.localIP().toString());
    Serial.println("Signal Strength: " + String(WiFi.RSSI()) + " dBm");
    Serial.println("MAC Address: " + WiFi.macAddress() + "\n");
    vTaskDelay(5000 / portTICK_PERIOD_MS);
  }
}
void ledTask(void *parameter) {
  while (true) {
    digitalWrite(LED_BUILTIN, HIGH);
    vTaskDelay(666 / portTICK_PERIOD_MS);
    digitalWrite(LED_BUILTIN, LOW);
    vTaskDelay(666 / portTICK_PERIOD_MS);
  }
}