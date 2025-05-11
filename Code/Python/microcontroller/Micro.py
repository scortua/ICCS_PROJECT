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
import time, network, requests, gc, random, reyax, _thread
from machine import Pin, Timer, ADC, UART, PWM
from neopixel import Neopixel
from PicoDHT22 import PicoDHT22

# Configuración de pines
RX_PIN = 1                              # pin de recepción LoRa
TX_PIN = 0                              # pin de transmisión LoRa
DHT_PIN = Pin(2, Pin.IN, Pin.PULL_UP)  # pin del sensor DHT22
MQ135_PIN = Pin(28, Pin.IN)             # pin del sensor MQ135
YL_PIN = Pin(26, Pin.IN)                # pin del sensor de ambiente (MQ135)
PUMP_PIN = Pin(15)                       # pin de la bomba de agua
PUMP_FREQ = 1000                        # frecuencia de la bomba
FAN_FREQ = 25000                        # frecuencia de la ventilador
FAN_PIN = Pin(16)                        # pin del ventilador
NEO_PIN = 17                             # pin del strip de LEDs
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

timer_sensors = Timer()

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
    print("\nConectado a la red wifi")        # imprimir mensaje de conexión

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
    # Set first 6 LEDs to color1
    for i in range(NUMPIXELS//2):
        strip.set_pixel(i, color1)
    # Set last 6 LEDs to color2
    for i in range(NUMPIXELS//2, NUMPIXELS):
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
    data = str(temperature) + ',' + str(humidity) + ',' + str(ppm) + ',' + str(ground) + ',' + str(led_rgb) + ',' + str(pump_)
    print(f"\nEnviando datos: {data}")
    lora.send(2,data.encode("utf-8"))  # Enviar datos por LoRa

# Función para controlar la bomba de agua
def write_pump():
    global ppm, ground
    ground_dry_threshold = 1.0  # Below this value is considered dry soil
    ppm_low_threshold = 1.0     # Below this value is considered low air quality
    # Calculate how dry the soil is (0 = wet, 100 = completely dry)
    dryness_percent = max(0, min(100, (1 - ground/3.3) * 100))
    # Calculate air quality percentage (0 = good, 100 = poor)
    air_quality_percent = max(0, min(100, ppm/3.3 * 100))
    # Combined score (weighted average: 70% soil, 30% air)
    watering_need = 0.7 * dryness_percent + 0.3 * air_quality_percent
    # Set pump duty cycle based on watering need (in 5% increments up to 40%)
    # 40% to 0% (0 = fully on, 65535 = fully off)
    if watering_need < 20:
        # Less than 20% need - pump off
        duty = 65535  # Fully OFF (PWM = 0%)
        pump_percent = 0
    elif watering_need < 30:
        # 20-30% need - pump 5%
        duty = int(65535 * 0.95)  # 95% off = 5% on
        pump_percent = 5
    elif watering_need < 40:
        # 30-40% need - pump 10%
        duty = int(65535 * 0.90)  # 90% off = 10% on
        pump_percent = 10
    elif watering_need < 50:
        # 40-50% need - pump 15%
        duty = int(65535 * 0.85)  # 85% off = 15% on
        pump_percent = 15
    elif watering_need < 60:
        # 50-60% need - pump 20%
        duty = int(65535 * 0.80)  # 80% off = 20% on
        pump_percent = 20
    elif watering_need < 70:
        # 60-70% need - pump 25%
        duty = int(65535 * 0.75)  # 75% off = 25% on
        pump_percent = 25
    elif watering_need < 80:
        # 70-80% need - pump 30%
        duty = int(65535 * 0.70)  # 70% off = 30% on
        pump_percent = 30
    elif watering_need < 90:
        # 80-90% need - pump 35%
        duty = int(65535 * 0.65)  # 65% off = 35% on
        pump_percent = 35
    else:
        # 90-100% need - pump 40% (maximum)
        duty = int(65535 * 0.60)  # 60% off = 40% on
        pump_percent = 40
    # Apply duty cycle to pump
    pump.duty_u16(duty)
    pump_ = f'la bomba esta al {pump_percent}%'
    # Debug output
    print(f"\tPump: ground={ground:.2f}, ppm={ppm:.2f}, need={watering_need:.1f}%, duty={pump_percent}%")

# Función para controlar el ventilador
def write_fan():
    global temperature, humidity
    # PI Controller for fan
    # Define setpoints and constants
    temp_setpoint = 25.0   # Desired temperature in Celsius
    humid_setpoint = 60.0  # Desired humidity percentage
    # Calculate how warm the environment is (0 = cool, 100 = too hot)
    temp_percent = max(0, min(100, (temperature - 20) * 10))  # 20°C is comfortable, 30°C is hot (100%)
    # Calculate humidity difference (0 = good, 100 = too humid)
    humid_percent = max(0, min(100, (humidity - humid_setpoint) * 2.5))
    # Combined score (weighted average: 60% temperature, 40% humidity)
    fan_need = 0.6 * temp_percent + 0.4 * humid_percent
    # Set fan duty cycle based on needs in 5% increments
    # Fan starts at 60% power minimum
    if fan_need < 20:
        # Less than 20% need - fan off
        duty = 0
        fan_percent = 0
    elif fan_need < 30:
        # 20-30% need - fan 60%
        duty = int(0.60 * 65535)
        fan_percent = 60
    elif fan_need < 40:
        # 30-40% need - fan 65%
        duty = int(0.65 * 65535)
        fan_percent = 65
    elif fan_need < 50:
        # 40-50% need - fan 70%
        duty = int(0.70 * 65535)
        fan_percent = 70
    elif fan_need < 60:
        # 50-60% need - fan 75%
        duty = int(0.75 * 65535)
        fan_percent = 75
    elif fan_need < 70:
        # 60-70% need - fan 80%
        duty = int(0.80 * 65535)
        fan_percent = 80
    elif fan_need < 80:
        # 70-80% need - fan 85%
        duty = int(0.85 * 65535)
        fan_percent = 85
    elif fan_need < 90:
        # 80-90% need - fan 90%
        duty = int(0.90 * 65535)
        fan_percent = 90
    else:
        # 90-100% need - fan 100%
        duty = 65535
        fan_percent = 100
    # Apply duty cycle to fan
    fan.duty_u16(duty)
    # Debug output
    print(f"\tFan: temp={temperature:.1f}, humid={humidity:.1f}, need={fan_need:.1f}%, duty={fan_percent}%")

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

main_loop()  # Start the main loop