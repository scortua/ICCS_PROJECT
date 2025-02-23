#include <SoftwareSerial.h>
#include <vector>

#define RX 1
#define TX 0

SoftwareSerial myserial(RX, TX); // RX, TX

#define LED_PIN 25

String rxData;
int VarInMsg = 6; // Número de variables en el mensaje
int commasInMsg = VarInMsg - 1;
int keyPos[8]; // Array para almacenar las posiciones de las comas

void send_ms(String ms) {
    myserial.println(ms); // mandar mensaje
    Serial.println(ms);   // imprimir mensaje
    delay(500);
    while (myserial.available()) {
        Serial.print(char(myserial.read())); // Si hay respuesta imprimirla en el monitor serial
    }
}

void init_lora() {
    Serial.println("\nConfigurando parametro antena LoRa\n");
    delay(2000);
    send_ms("AT"); // verificar estado de comandos
    delay(1000);
    send_ms("AT+ADDRESS=2"); // colocar direccion lora 0 - 65535
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
    // inicializa el lora
    init_lora();
}

void loop() {
    while (myserial.available()) {
        rxData = myserial.readString();
    }
    rxData.trim();                // Eliminar espacios antes y después del mensaje
    rxData.replace("+RCV=", "");  // Eliminar "+RCV=" del mensaje

    // Detectar las comas del mensaje recibido
    keyPos[0] = 0; // Inicializar la primera posición
    for (int i = 1; i <= commasInMsg; i++) {
        keyPos[i] = rxData.indexOf(',', keyPos[i - 1] + 1);
    }

    // Obtener el valor de las variables del mensaje
    String txId = rxData.substring(0, keyPos[1]);
    String dataLen = rxData.substring(keyPos[1] + 1, keyPos[2]);
    String Temperature = rxData.substring(keyPos[2] + 1, keyPos[3]);
    String Humedity = rxData.substring(keyPos[3] + 1, keyPos[4]);
    String rssi = rxData.substring(keyPos[4] + 1, keyPos[5]);
    String snr = rxData.substring(keyPos[5] + 1);

    // Imprimir el mensaje recibido del transmisor
    Serial.println(rxData);

    // Imprimir la posición de las comas del mensaje
    Serial.print("Posición de las comas:");
    for (int i = 1; i <= commasInMsg; i++) {
        Serial.print(keyPos[i]);
        Serial.print(" ");
    }
    Serial.println();

    // Imprimir las variables del mensaje
    Serial.print("TxId: " + txId);
    Serial.print(" Length: " + dataLen);
    Serial.print(" Temp: " + Temperature);
    Serial.print(" Hume: " + Humedity);
    Serial.print(" RSSI: " + rssi);
    Serial.println(" SNR: " + snr);

    digitalWrite(LED_PIN, HIGH);
    delay(4000);
    digitalWrite(LED_PIN, LOW);
    delay(1000);
}