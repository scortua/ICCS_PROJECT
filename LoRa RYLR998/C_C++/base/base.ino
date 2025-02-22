#include <SoftwareSerial.h>

// Configuración de la UART
SoftwareSerial myserial(13, 14); // RX, TX

String rxData = "";
int VarInMs = 6; // variables recibidas en el mensaje
int commasInMs = VarInMs - 1;
int keyPos[8]; // Array para almacenar las posiciones de las comas

void send_ms(String ms)
{
    myserial.println(ms); // enviar mensaje
    Serial.println(ms);
    delay(500);
    while (myserial.available())
    {
        Serial.print(char(myserial.read())); // Si hay respuesta imprimirla en el monitor serial
    }
}

void init_lora()
{
    Serial.println("\nConfigurando parametro antena LoRa\n");
    delay(2000);
    send_ms("AT"); // verificar estado de comandos
    delay(1000);
    send_ms("AT+RESET"); // resetea valores de lora
    delay(1000);
    send_ms("AT+IPR?"); // verificacion baudrate
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

void setup()
{
    Serial.begin(115200);
    myserial.begin(115200);
    delay(5000);
    // Inicializar LoRa
    init_lora();
}

void loop()
{
    while (myserial.available())
    {
        rxData = myserial.readString();
    }
    rxData.trim();               // Eliminar espacios antes y después del mensaje
    rxData.replace("+RCV=", ""); // Eliminar "+RCV=" del mensaje

    // Detectar las comas del mensaje recibido
    keyPos[0] = 0; // Inicializar la primera posición
    for (int i = 1; i <= commasInMs; i++)
    {
        keyPos[i] = rxData.indexOf(",", keyPos[i - 1] + 1);
    }

    // obtener las variables del mensaje
    String txId = rxData.substring(0, keyPos[1]);
    String dataLen = rxData.substring(keyPos[1] + 1, keyPos[2]);
    String Temperature = rxData.substring(keyPos[2] + 1, keyPos[3]);
    String Humedity = rxData.substring(keyPos[3] + 1, keyPos[4]);
    String rssi = rxData.substring(keyPos[4] + 1, keyPos[5]);
    String snr = rxData.substring(keyPos[5] + 1);

    // Imprimir el mensaje recibido del transmisor
    Serial.println(rxData);

    Serial.print("TxId: " + txId);
    Serial.print(" Length: " + dataLen);
    Serial.print(" Temp: " + Temperature);
    Serial.print(" Hume: " + Humedity);
    Serial.print(" RSSI: " + rssi);
    Serial.println(" SNR: " + snr);

    if (Temperature.toFloat() < 0 && Humedity.toFloat() < 0)
    {
        Serial.println("Error en la lectura de los sensores");
    }
    else
    {
        Serial.print("TxId: " + txId);
        Serial.print(" Length: " + dataLen);
        Serial.print(" Temp: " + Temperature);
        Serial.print(" Hume: " + Humedity);
        Serial.print(" RSSI: " + rssi);
        Serial.println(" SNR: " + snr);

        // Guardar en la base de datos
        // Aquí deberías usar una biblioteca específica para MySQL en Arduino
        // String query = "INSERT INTO DHT22 (temperature, humidity) VALUES ('" + Temperature + "', '" + Humedity + "')";
        // if (mysql_query(conn, query.c_str()))
        // {
        //     Serial.println("Error al insertar en la base de datos");
        // }
        // else
        // {
        //     Serial.println("Datos insertados en la base de datos");
        // }
    }
}
