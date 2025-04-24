#include <FreeRTOS.h>
#include <task.h>
#include <SoftwareSerial.h>

#define RX 1
#define TX 0
SoftwareSerial myserial(RX,TX);

void init_lora();
void send_ms(String ms);
void lora_init(void *parameter);
void blink(void *parameter);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  myserial.begin(115200);
  xTaskCreate(lora_init, "lora_init", 300, nullptr, 2, nullptr);
  xTaskCreate(blink, "blink", 128, nullptr, 1, nullptr);
}

void loop(){}

void init_lora() {
  delay(2000);
  Serial.println("\nConfigurando parametro antena LoRa\n");
  delay(1000);
  send_ms("AT"); // verificar estado de comandos
  delay(500);
  send_ms("AT+ADDRESS=1"); // colocar direccion lora 0 - 65535
  delay(500);
  send_ms("AT+NETWORKID=5"); // colocando direccion de red
  delay(500);
  send_ms("AT+PARAMETER=9,7,1,12"); // RF parameters
  delay(500);
  send_ms("AT+MODE?"); // operation mode
  delay(500);
  send_ms("AT+CPIN?"); // contraseña
  delay(500);
}
void send_ms(String ms) {
    myserial.println(ms); // mandar mensaje
    Serial.println(ms); // imprimir mensaje
    delay(500);
    while (myserial.available()) {
        Serial.print(char(myserial.read()));  // Si hay respuesta imprimirla en el monitor serial 
    }
}
void lora_init(void *parameter){
  (void)parameter; // Evitar advertencias de compilación
  init_lora();
  String data = "Hello World";
  String datalen = String(data.length());
  Serial.println("Sending data: " + datalen + "," + data);
  while(1){
    send_ms("AT+SEND=2," + datalen + "," + data); // Enviar datos
    delay(2000);
  }
  //vTaskDelete(NULL); // Eliminar la tarea
}
void blink(void *parameter){
  (void)parameter; // Evitar advertencias de compilación
  pinMode(LED_BUILTIN, OUTPUT);
  while(1){
    digitalWrite(LED_BUILTIN, LOW);
    delay(333);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(333);
  }
  //vTaskDelete(NULL); // Eliminar la tarea
}