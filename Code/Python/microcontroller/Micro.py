"""
ICCS - ESCUELA COLOMBIANA DE INGENIERIA JULIO GARAVITO
Proyecto: Sistema de monitoreo de invernadero

se usa para el microcontrolador pico 2w
------------------- 3.3 voltios ------------------
dht22: sensor de temperatura y humedad 3.3v - digital/analogo
lora rylr998: modulo de comunicacion 3.3v - digital
yl-100: sensor de calidad de suelo 3.3v - digital/analogo
------------------ 5 voltios ---------------------
mq135: sensor de calidad de aire 5v - digital/analogo
neopixel: tira de leds rgb 5v - pwm digital
------------------ 12 voltios --------------------
ventilador: ventilador de 12v - pwm digital
bomba: bomba de agua 12v - pwm digital

------------------ proper ------------------------
wifi -> mqtt?

"""

import time, network, gc, random
from machine import Pin, Timer, ADC, UART, PWM
from neopixel import Neopixel
from PicoDHT22 import PicoDHT22

# Configuración de pines
RX_PIN = 1                              # pin de recepción LoRa
TX_PIN = 0                              # pin de transmisión LoRa
DHT_PIN = Pin(16, Pin.IN, Pin.PULL_UP)  # pin del sensor DHT22
MQ135_PIN = Pin(28, Pin.IN)             # pin del sensor MQ135
YL_PIN = Pin(26, Pin.IN)                # pin del sensor de ambiente (MQ135)
PUMP_PIN = Pin(3)                       # pin de la bomba de agua
PUMP_FREQ = 1000                        # frecuencia de la bomba
FAN_FREQ = 25000                        # frecuencia de la ventilador
FAN_PIN = Pin(4)                        # pin del ventilador
NEO_PIN = 2                             # pin del strip de LEDs
NUMPIXELS = 12                          # número de LEDs en el strip
# Define colors for the LEDs (R, G, B) values from 0-255
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
OFF = (0, 0, 0)

# Variables globales
temperature = 0.0   # Temperatura en °C
humidity = 0.0      # Humedad en %
ppm = 0             # PPM del sensor MQ135    
ground = 0          # Valor del sensor YL-100

# Inicialización de dispositivos
uart0 = UART(0, baudrate=115200, tx=Pin(TX_PIN), rx=Pin(RX_PIN))  # Inicializar UART para LoRa
dht_sensor = d = PicoDHT22(DHT_PIN)  # Inicializar sensor DHT22
mq_sensor = ADC(MQ135_PIN)  # Inicializar sensor MQ135
yl_sensor = ADC(YL_PIN)  # Inicializar sensor de ambiente (MQ135)
pump = PWM(PUMP_PIN, PUMP_FREQ)  # Inicializar bomba
fan = PWM(FAN_PIN, FAN_FREQ)  # Inicializar ventilador
strip = Neopixel(NUMPIXELS, 0, NEO_PIN, "GRB")  # Inicializar strip de LEDs
strip.brightness(10)  # Inicializar brillo del strip de LEDs

def wifi():
    # wifi
    ssid = 'CARPE_DIEM'           # nombre de la red wifi
    password = 'Oing9002'   # contraseña de la red wifi
    # wifi interface
    wifi = network.WLAN(network.STA_IF)    # interfaz wifi
    wifi.active(True)                      # activar la interfaz wifi
    # conectar a la red wifi
    while True:
        wifi.connect(ssid, password)          # conectar a la red wifi
        if wifi.isconnected():                # si está conectado
            break                             # salir del bucle
    print("Conectado a la red wifi")        # imprimir mensaje de conexión

# Function to update the LED strip with two different colors
def update_led_strip(color1, color2):
    # Set first 6 LEDs to color1
    for i in range(6):
        strip.set_pixel(i, color1)
    # Set last 6 LEDs to color2
    for i in range(6, NUMPIXELS):
        strip.set_pixel(i, color2)
    # Apply the changes
    strip.show()

# Función para encender los timers
def on_timers():
    timer_dht = Timer(-1)   # Inicializar timer para DHT22
    timer_mq135 = Timer(-1) # Inicializar timer para MQ135
    timer_ground = Timer(-1)  # Inicializar timer para el sensor de ambiente
    timer_dht.init(period=4800, mode=Timer.PERIODIC, callback=read_dht)  # Cada 4800 ms
    timer_mq135.init(period=5100, mode=Timer.PERIODIC, callback=read_mq135)  # Cada 5100 ms
    timer_ground.init(period=4900, mode=Timer.PERIODIC, callback=read_ground)  # Cada 4900 ms

# Función para simular el envío de datos a LoRa
def send_to_lora(ms):
    uart0.write(ms + "\r\n")        # Enviar mensaje
    time.sleep(0.22)                 # Esperar medio segundo   
    rec = bytes()                   # Inicializar variable de recepción
    while uart0.any() > 0:          # Mientras haya datos en el buffer
        rec += uart0.read(1)        # Leer un byte y concatenar
    print(rec.decode('utf-8'))      # Imprimir el mensaje recibido

def init_lora():
    time.sleep(1)  # Esperar un segundo para la inicialización
    print("LoRa inicializado")
    time.sleep(1)  # Esperar un segundo para la inicialización
    send_to_lora("AT")
    time.sleep(0.2)  
    send_to_lora("AT+ADDRESS=1")
    time.sleep(0.2)
    send_to_lora("AT+NETWORKID=5")
    time.sleep(0.2)
    send_to_lora("AT+PARAMETER=9,7,1,12")
    time.sleep(0.2)

# Función para leer el sensor DHT22
def read_dht(timer):
    global temperature, humidity, c_dht
    temperature, humidity = dht_sensor.read()  # Leer el sensor DHT22
    if temperature is None or humidity is None:
        temperature = random.uniform(20, 30)  # Simular temperatura
        humidity = random.uniform(40, 60)     # Simular humedad

# Función para leer el sensor MQ135
def read_mq135(timer):
    global ppm
    valor = mq_sensor.read_u16() # Leer el valor del sensor MQ135
    ppm = (valor / 65535) * 3.3  
    
# Función para leer el valor de ambiente
def read_ground(timer):
    global ground
    valor = yl_sensor.read_u16()  # Leer el valor del sensor de ambiente
    ground = (valor / 65535) * 3.3  

def write_pump():
    global ppm, ground
    if ppm > 1 and ground > 1:  # Si el valor de ppm y ground son menores a 0.5
        pump.duty_u16(512)
    elif ppm < 1 and ground < 1:
        pump.duty_u16(1023)
    else:
        pump.duty_u16(0)

def write_fan():
    global temperature, humidity
    if temperature > 30 and humidity < 50:  # Si la temperatura es mayor a 30 y la humedad menor a 50
        fan.duty_u16(512)  # Encender el ventilador al 50%
    elif temperature < 30 and humidity > 50:
        fan.duty_u16(1023)  # Encender el ventilador al 100%
    else:
        fan.duty_u16(0)  # Apagar el ventilador

def main_loop():
    global temperature, humidity, ppm, ground
    init_lora()  # Inicializar LoRa
    on_timers()  # Encender los timers
    while True:
        update_led_strip(RED, PURPLE)  # Update the LED strip with the current colors
        write_fan()
        write_pump()
        # Format the data as a string with all global parameters
        info = str(temperature) + ',' + str(humidity) + ',' + str(ppm) + ',' + str(ground)
        data = "AT+SEND=0," + str(len(info)) + ',' + info
        print(f"\nEnviando datos: {data}")
        send_to_lora(data)  # Send the data through LoRa
        time.sleep(10)  # Keep the program running
        gc.collect()    # Collect garbage to free up memory
        print(f"Memoria libre: {gc.mem_free()} bytes") # Print free memory

main_loop()  # Start the main loop