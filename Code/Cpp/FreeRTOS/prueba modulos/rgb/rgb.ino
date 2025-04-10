#include <FreeRTOS.h>
#include <task.h>

#include <Adafruit_NeoPixel.h>
#define PIN 2
#define NUMPIXELS 22
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
uint8_t brightness = 0;

void neopixel(void *parameter);
void blink(void *parameter);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT); // Initialize the LED_BUILTIN pin as an output
  pixels.begin(); // Initialize the NeoPixel strip
  // create tasks
  xTaskCreate(neopixel, "neopixel", 1000, NULL, 2, NULL);
  xTaskCreate(blink, "blink", 128, NULL, 1, NULL);
}

void loop() {}

void neopixel(void *parameter){
  (void)parameter; // Avoid unused parameter warning
  bool increasing = true;
  pixels.setPixelColor(0, pixels.Color(0, 255, 255)); // led, rojo, verde, azul
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
    pixels.setBrightness(brightness);
    pixels.show();
    vTaskDelay(333 / portTICK_PERIOD_MS);
  }
}
void blink(void *parameter){
  (void)parameter; // Avoid unused parameter warning
  while(1){
    digitalWrite(LED_BUILTIN, HIGH); // Turn the LED on (HIGH is the voltage level)
    vTaskDelay(500 / portTICK_PERIOD_MS); // Wait for a second
    digitalWrite(LED_BUILTIN, LOW); // Turn the LED off by making the voltage LOW
    vTaskDelay(500 / portTICK_PERIOD_MS); // Wait for a second
  }
}