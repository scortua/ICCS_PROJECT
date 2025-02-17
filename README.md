![Badge en desarrollo](https://img.shields.io/badge/STATUS-EN%20DESAROLLO-green) ![Badge License](https://img.shields.io/badge/License-MIT-yellow)

![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![C++](https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white) ![C](https://img.shields.io/badge/c-%2300599C.svg?style=for-the-badge&logo=c&logoColor=white) ![Raspberry Pi](https://img.shields.io/badge/-Raspberry_Pi-C51A4A?style=for-the-badge&logo=Raspberry-Pi) ![LoRaWAN](https://img.shields.io/badge/LoRaWAN-blue?style=for-the-badge&logo=lorawan&logoColor=white)

[![Escuela Colombiana Ingenieros](Images/Logotipo_eci.png)](https://www.escuelaing.edu.co/)

# ICCS_PROJECT
Proyecto de internet de las cosas con convergencia en la ciberseguridad. Propósito de tener un proyecto que obtenga señales físicas y se actúe a esas señales a partir de un microcontrolador y que se use un tipo de comunicación muy usado mundialmente, para conectarse a un servidor local que permita guardar los datos y mantenerlos seguros.

## Índice
* [Propuesta Proyecto](#-PROYECTO-PROPUESTO)
* [Componentes a Usar](#componentes-a-usar)
* [LoRa](#LoRa)
* [Función Sensores](#Función-Sensores)
* [Conexiones](#conexiones)
* [Base de datos local](#base-datos-local)
* [Licencia](#licencia)


## PROYECTO PROPUESTO


## Componentes a Usar
<details>
<summary>LoRa RYLR998</summary>

### Modulo lora

[![LoRa](Images/rylr998.png)](https://www.amazon.com/-/es/M%C3%B3dulo-interfaz-RYLR998-certificaci%C3%B3n-antena/dp/B099RM1XMG)

Modulo lora que funciona por _UART_ siendo muy versátil y útil para microcontroladores simples. La forma en la que funciona este modulo es por comandos que el mismo fabricante recomienda usar y se pueden ver en el [manual](Documents/LoRa_AT_Command_RYLR998_RYLR498_EN.pdf).

Básicos comandos a usar:

>"AT" -> Verificación de conectividad
>"AT+ADDRESS" -> Indicar dirección 
>"AT+NETWORKID" -> Indicar dirección de red
>"?" -> Al final de cualquier comando para verificar default

</details>

<details>
<summary> RP PICO </summary>

### Raspberry pi pico

[![PI PICO](Images/pi_pico.png)](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#pico-1-family)

La **Raspberry Pi Pico** es una placa de desarrollo económica y versátil basada en el microcontrolador **RP2040**, diseñado por Raspberry Pi. Es ideal para proyectos de electrónica, IoT, robótica y más.

- **Procesador Dual-Core ARM Cortex-M0+** a 133 MHz.
- **264 KB de SRAM** integrada.
- **2 MB de memoria Flash** en la placa (en el modelo estándar).
- **DMA (Direct Memory Access)** para transferencias de datos eficientes.
- **26 pines GPIO** multifuncionales.
- Soporte para **PWM**, **I2C**, **SPI**, **UART** y **ADC**.
- **3 entradas analógicas** (12-bit ADC).
Voltaje de operación: **1.8V a 5.5V**.
- Conector **Micro-USB** para alimentación y programación.
- Modo de bajo consumo (**Sleep** y **Dormant**).
- Soporte nativo para **MicroPython** y **C/C++**

Pequeño ejemplo en micropython para encender y apagar progresivamente el led incluido en la tarjeta.
```python
import time
from machine import Pin, PWM

pwm = PWM(Pin(25))

pwm.freq(1000)

duty = 0
direction = 1
while True:
    duty += direction
    if duty > 255:
        duty = 255
        direction = -1
    elif duty < 0:
        duty = 0
        direction = 1
    pwm.duty_u16(duty * duty)
    time.sleep(0.001)
```
</details>

<details>
<summary> RPI4 </summary>

### Raspberry pi 4

[![RPI4](Images/pi4.png)](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/specifications/)

La **Raspberry Pi 4** es una potente computadora de placa única (SBC) diseñada para una amplia gama de aplicaciones, desde proyectos educativos hasta servidores domésticos y sistemas embebidos. Es la versión más avanzada de la serie Raspberry Pi, con mejoras significativas en rendimiento y conectividad.

- **Procesador Broadcom BCM2711** con CPU Quad-Core ARM Cortex-A72 a **1.5 GHz**.
- Opciones de memoria RAM: **2 GB**, **4 GB** u **8 GB** (LPDDR4).
- Soporte para **microSD** (arranque del sistema operativo).
- **2 puertos USB 3.0** y **2 puertos USB 2.0** para dispositivos externos.
- Compatible con almacenamiento externo vía USB o SSD.
- **Doble banda Wi-Fi (2.4 GHz y 5 GHz)** y **Bluetooth 5.0**.
- **Gigabit Ethernet** para conexiones de red de alta velocidad.
- **2 puertos HDMI** (soporte para resoluciones de hasta **4K**).
- GPU **VideoCore VI** para aceleración gráfica y de video.
- Soporte para decodificación de video **4K H.265**.
- Salida dual HDMI para configuraciones de pantalla múltiple.
- **40 pines GPIO** compatibles con versiones anteriores.
- Soporte para **I2C**, **SPI**, **UART**, **PWM** y más.
- Voltaje de entrada: **5V** mediante conector **USB-C**.
- Consumo de energía optimizado para proyectos embebidos.

[Descripción pines python](https://gpiozero.readthedocs.io)

```python
from gpiozero import LED
from time import sleep

led = LED(17)  # Conectar un LED al pin GPIO 17

while True:
    led.on()   # Encender el LED
    sleep(1)   # Esperar 1 segundo
    led.off()  # Apagar el LED
    sleep(1)   # Esperar 1 segundo
```
</details>

<details>

<summary>Temperatura y Humedad DHT22</summary>

## DHT22

[![DHT22](Images/DHT22-Sensor-Pinout.png)](https://www.instructables.com/Raspberry-Pi-Pico-DHT22-AM2302-Temperature-Sensor-/)

El DHT22 es un sensor digital que mide la temperatura y la humedad relativa del ambiente. Es muy utilizado en proyectos de electrónica, IoT y automatización del hogar debido a su precisión y facilidad de uso.

Características Principales
Rango de medición de temperatura: -40°C a 80°C (±0.5°C de precisión).

Rango de medición de humedad: 0% a 100% (±2% de precisión).

Salida digital: Proporciona los datos en formato digital, lo que facilita su lectura con microcontroladores como Arduino, Raspberry Pi, ESP8266, etc.

Frecuencia de muestreo: Realiza una medición cada 2 segundos (no es recomendable leerlo más rápido).

Alimentación: Funciona con un voltaje de 3.3V a 5V.

Conexión: Tiene 3 o 4 pines (dependiendo del modelo):

VCC: Alimentación (3.3V o 5V).

GND: Conexión a tierra.

Data: Pin de comunicación digital (envía los datos al microcontrolador).

NC (opcional): Pin no conectado (no se usa).

</details>

## LoRa
![LoRaWAN](Images/LoRaWAN_Logo.png)
 
Los módulos LoRa (Long Range) son dispositivos de comunicación inalámbrica diseñados para transmitir datos a largas distancias con bajo consumo de energía. Son ampliamente utilizados en aplicaciones de Internet de las Cosas (IoT) debido a su capacidad para conectar dispositivos en áreas extensas y de difícil acceso.

¿Qué es LoRa?
LoRa es una tecnología de modulación inalámbrica que permite la comunicación de largo alcance (hasta varios kilómetros en áreas abiertas) con un bajo consumo de energía. Utiliza frecuencias de radio libres (como 868 MHz en Europa o 915 MHz en América) y es ideal para aplicaciones donde no se requiere una alta velocidad de transmisión, pero sí una gran cobertura y eficiencia energética.

- LoRaWAN es un protocolo de red que utiliza la tecnología LoRa para conectar dispositivos IoT a servidores en la nube. Proporciona:
- Seguridad: Cifrado de extremo a extremo.
- Escalabilidad: Soporta miles de dispositivos en una misma red.
- Modos de operación: Clase A (bajo consumo), Clase B (latencia controlada) y Clase C (sin latencia).

## Función Sensores

<details>
<summary>Temperatura y Humedad</summary>

</details>

<details>
<summary>Ventilación</summary>

</details>

<details>
<summary>Ultravioleta</summary>

</details>


## Conexiones


## Base datos local

Se usa _mariadb_ para la crear las bases de datos porque es una extensión de _mysql_.

Primero se actualiza el sistema
```bash
sudo apt-get update
sudo pat-get upgrade
```

Se descarga mariaDB-mysql en la raspberry pi 4.
```bash
sudo apt install mariadb-server 
```

Se descarga el complemento para _python_.
```bash
sudo apt-get install python-mysqldb
```

<details>
<summary>Enlace a servidor local</summary>

Ingresamos al host de mysql.
```bash
sudo mysql -u root
```
Creamos la base de datos del ***Invernadero***
```SQL
CREATE DATABASE Invernadero;
```
Nos adentramos en la base de datos
```SQL
USE Invernadero;
```
Creamos la tabla DHT22
```SQL
CREATE TABLE DHT22 (time TIMESTAMP, Temperatura FLOAT, Humedad FLOAT);
```
Ahora es mostrar la tabla
```SQL
DESCRIBE DHT22;
```
Ahora, se crea el usuario host
```SQL
CREATE USER 'RPI4'@'localhost' IDENTIFIED BY 'raspberry4';
```
Se otorgan permisos
```SQL
GRANT ALL PRIVILEGES ON *.* TO 'RPI4'@'localhost';
```
Para ver las bases de datos se usa:
```SQL
SHOW DATABASES;
SHOW TABLES;
```
Y para conectar la base de datos al sistema con python
```Python
name_db = MYSQLdb.connect(host="localhost",user="RPI4",passwd="1234567890",db="Invernadero") #conexión con MYSQL/MariaDB 
cursor = db.cursor() # crear cursor

cursor.execute(f"INSERT INTO Data (Temperatura, Humedad) VALUES ({temp}, {hum})") # ingresar datos
db.commit() # 
```
Para verificar lo que ha pasado en la base de datos se va a SQL
```SQL
SELECT * FROM DHT22;
```

</details>

<details>
<summary>Enlace a servidor web</summary>

<details>

## Licencia

