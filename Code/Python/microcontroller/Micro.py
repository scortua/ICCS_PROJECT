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
wifi -> mqtt and HTTP
"""
import time, network, ssl, requests, gc, random, reyax
from machine import Pin, Timer, ADC, UART, PWM
from umqtt.simple import MQTTClient
from neopixel import Neopixel
from PicoDHT22 import PicoDHT22

# Configuración de pines
RX_PIN = 1                              # pin de recepción LoRa
TX_PIN = 0                              # pin de transmisión LoRa
DHT_PIN = Pin(2, Pin.IN, Pin.PULL_UP)   # pin del sensor DHT22
MQ135_PIN = Pin(26, Pin.IN)             # pin del sensor MQ135
YL_PIN = Pin(28, Pin.IN)                # pin del sensor de ambiente (MQ135)
PUMP_PIN = Pin(15)                      # pin de la bomba de agua
PUMP_FREQ = 25000                       # frecuencia de la bomba
FAN_FREQ = 1000                         # frecuencia de la ventilador
FAN_PIN = Pin(16)                       # pin del ventilador
NEO_PIN = 3                             # pin del strip de LEDs
NUMPIXELS = 24                          # número de LEDs en el strip
# Define colors for the LEDs (R, G, B) values from 0-255
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
OFF = (0, 0, 0)
# Define mqtt broker
MQTT_SERVER = "192.168.1.65"  # MQTT broker address
MQTT_PORT = 1883  # Port for secure MQTT connection
MQTT_CLIENT_ID = "Invernadero"  # Unique client ID for the MQTT client
MQTT_USER = "Invernadero"  # MQTT username (if required)
MQTT_PASSWORD = "1234567890"  # MQTT password (if required)

# Variables globales
temperature = 0.0   # Temperatura en °C
humidity = 0.0      # Humedad en %
ppm = 0             # PPM del sensor MQ135    
ground = 0          # Valor del sensor YL-100
led_rgb = 'off'     # Color del LED
pump_ = 'off'       # Estado de la bomba
url = 'https://api.openweathermap.org/data/2.5/weather?q=Bogota,CO&units=metric&appid=69285e08908ba2461be431c348d1e02d'
# Inicialización de dispositivos
uart0 = UART(0, baudrate=115200, tx=Pin(TX_PIN), rx=Pin(RX_PIN))  # Inicializar UART para LoRa
lora = reyax.RYLR998(uart0)  # Inicializar LoRa
lora.pulse
lora.networkid = 5  # ID de la red LoRa
lora.address = 1  # Dirección del nodo
lora.rf_parameters = (9,7,1,12)
dht_sensor = d = PicoDHT22(DHT_PIN)  # Inicializar sensor DHT22
mq_sensor = ADC(MQ135_PIN)  # Inicializar sensor MQ135
yl_sensor = ADC(YL_PIN)  # Inicializar sensor de ambiente (MQ135)
pump = PWM(PUMP_PIN, PUMP_FREQ)  # Inicializar bomba
fan = PWM(FAN_PIN, FAN_FREQ)  # Inicializar ventilador
strip = Neopixel(NUMPIXELS, 0, NEO_PIN, "GRB")  # Inicializar strip de LEDs
strip.brightness(100)  # Inicializar brillo del strip de LEDs

client = MQTTClient(
    client_id=MQTT_CLIENT_ID,
    server=MQTT_SERVER,
    port=MQTT_PORT,
    user=MQTT_USER,
    password=MQTT_PASSWORD
    )

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
        print(".", end="")  # print a dot without line break
        if wifi.isconnected():                # si está conectado
            break                             # salir del bucle
        time.sleep(0.5)                     # esperar 0.5 segundos
    print("\nConectado a la red wifi")        # imprimir mensaje de conexión

def mqtt():
    global temperature, humidity, ppm, ground, pump_, led_rgb
    client.connect()
    topic = "Invernadero"  # topic to publish
    msg = "{:.2f},{:.2f},{:.2f},{:.2f},{},{}".format(temperature, humidity, ppm, ground, led_rgb, pump_)  # message to publish
    client.publish(topic, msg)  # publish message
    client.disconnect()  # disconnect from MQTT broker

def extra():
    response = requests.get(url)  # hacer una solicitud GET a la API
    temp = 0  # inicializar temperatura
    hum = 0   # inicializar humedad
    try:
        if response.status_code == 200:  # si la solicitud fue exitosa
            response_json = response.json()  # convertir la respuesta a JSON
            temp = response_json['main']['temp']  # obtener la temperatura
            hum = response_json['main']['humidity']  # obtener la humedad
            response.close()  # cerrar la respuesta
    except Exception as e:
        print(f"Error al obtener datos de la API: {e}")
    return temp, hum  # devolver la temperatura y humedad

# Function to update the LED strip with two different colors
def update_led_strip(color1, color2):
    # Set even-indexed LEDs to color1 and odd-indexed LEDs to color2
    for i in range(NUMPIXELS):
        if i % 2 == 0:  # Even index
            strip.set_pixel(i, color1)
        else:  # Odd index
            strip.set_pixel(i, color2)
    # Apply the changes
    led_rgb = 'la tira de led es de color ' + str(color1) + ' y ' + str(color2)
    gc.collect()  # collect garbage
    strip.show()

# Función para leer el sensor DHT22
def read_sensors():
    global temperature, humidity, ppm, ground 
    # Read DHT22 sensor (temperature and humidity)
    temperature, humidity = dht_sensor.read()
    if temperature is None or humidity is None or temperature == 0 or humidity == 0:
        temperature, humidity = extra()
    # Read MQ135 sensor (air quality)
    mq_value = mq_sensor.read_u16()
    ppm = (mq_value / 65535) * 3.3
    # Read YL-100 sensor (soil moisture)
    yl_value = yl_sensor.read_u16()
    ground = (yl_value / 65535) * 3.3

# Función para enviar datos por LoRa
def lorra():
    global temperature, humidity, ppm, ground
    # Formatear los datos como una cadena con todos los parámetros globales
    data = f'{temperature:.2f},{humidity:.2f},{ppm:.2f},{ground:.2f},{led_rgb},{pump_}'
    print(f"\nEnviando datos: {data}")
    lora.send(2,data.encode("utf-8"))  # Enviar datos por LoRa

# Función para controlar la bomba de agua
def write_pump():
    global ground, pump_
    # 100% is off and 0% is on
    # Calculate the watering need based on soil moisture
    watering_need = (ground / 3.3) * 100
    # Calculate the duty cycle for the pump
    if watering_need < 15:
        pump_percent = 100
        duty = int(0.0 * 65535)
        pump_ = 'la bomba esta al 100%'
    elif watering_need > 40 and watering_need < 60:
        pump_percent = 35
        duty = int(0.35 * 65535)
        pump_ = 'la bomba esta al 35%'
    else:
        pump_percent = 0
        duty = int(1 * 65535)
        pump_ = 'la bomba esta al 0%'
    # Apply duty cycle to pump
    pump.duty_u16(duty)
    pump_ = f'la bomba esta al {pump_percent}%'
    # Debug output
    print(f"\tPump: ground={ground:.2f}, ppm={ppm:.2f}, need={watering_need:.1f}%, duty={pump_percent}%")

# Función para controlar el ventilador
def write_fan():
    global temperature, fan_
    # Define setpoint and constants
    temp_setpoint = 18   # Desired temperature in Celsius
    # Calculate the temperature difference (how much above setpoint)
    temp_diff = temperature - temp_setpoint
    # Fan control logic - activate when difference is at least 0.5°C
    if temp_diff < 0:
        # Temperature is below setpoint - fan off
        duty = 0
        fan_percent = 0
    elif temp_diff < 0.5:
        # Temperature is below or just slightly above setpoint - fan at minimum 10%
        duty = int(0.60 * 65535)
        fan_percent = 60
    elif temp_diff < 0.75:
        # Difference is 0.5-0.75°C - fan at 15%
        duty = int(0.65 * 65535)
        fan_percent = 65
    elif temp_diff < 1.0:
        # Difference is 0.75-1.0°C - fan at 20%
        duty = int(0.70 * 65535)
        fan_percent = 70
    elif temp_diff < 1.25:
        # Difference is 1.0-1.25°C - fan at 25%
        duty = int(0.75 * 65535)
        fan_percent = 75
    elif temp_diff < 1.5:
        # Difference is 1.25-1.5°C - fan at 30%
        duty = int(0.80 * 65535)
        fan_percent = 80
    elif temp_diff < 1.75:
        # Difference is 1.5-1.75°C - fan at 35%
        duty = int(0.85 * 65535)
        fan_percent = 85
    elif temp_diff < 2.0:
        # Difference is 1.75-2.0°C - fan at 40%
        duty = int(0.90 * 65535)
        fan_percent = 90
    elif temp_diff < 2.25:
        # Difference is 2.0-2.25°C - fan at 45%
        duty = int(0.95 * 65535)
        fan_percent = 95
    elif temp_diff < 2.5:
        # Difference is 2.25-2.5°C - fan at 50%
        duty = int(1 * 65535)
        fan_percent = 100
    else:
        # Difference is 2.75°C or more - fan at maximum 60%
        duty = int(1 * 65535)
        fan_percent = 100
    # Apply duty cycle to fan
    fan.duty_u16(duty)
    # Debug output
    print(f"\tFan: temp={temperature:.1f}, humid={humidity:.1f}, duty={fan_percent}%")

def main_loop():
    global temperature, humidity, ppm, ground
    wifi()  # Connect to WiFi
    read_sensors()  # Read initial sensor values
    while True:
        update_led_strip(RED, PURPLE)  # Update the LED strip with the current colors
        write_fan() # Control the fan based on temperature and humidity
        write_pump() # Control the pump based on ppm and ground
        lorra()
        time.sleep(33)  # Keep the program running
        gc.collect()    # Collect garbage to free up memory
        read_sensors()
        print(f"\nMemoria libre: {gc.mem_free()} bytes") # Print free memory
        mqtt()  # Send data to MQTT broker

main_loop()  # Start the main loop