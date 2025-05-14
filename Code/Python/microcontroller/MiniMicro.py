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
"""

import time, gc, random, reyax
from machine import Pin, ADC, UART, PWM
from neopixel import Neopixel
from PicoDHT22 import PicoDHT22

# Configuración de pines
DHT_PIN = Pin(2, Pin.IN, Pin.PULL_UP)  # pin del sensor DHT22
MQ135_PIN = Pin(28, Pin.IN)             # pin del sensor MQ135
YL_PIN = Pin(26, Pin.IN)                # pin del sensor de ambiente (YL-100)
PUMP_PIN = Pin(15)                      # pin de la bomba de agua
PUMP_FREQ = 25000                        # frecuencia de la bomba
FAN_FREQ = 1000                        # frecuencia del ventilador
FAN_PIN = Pin(16)                       # pin del ventilador
NEO_PIN = 17                            # pin del strip de LEDs
NUMPIXELS = 24                          # número de LEDs en el strip
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

# Inicialización de dispositivos
dht_sensor = PicoDHT22(DHT_PIN)  # Inicializar sensor DHT22
mq_sensor = ADC(MQ135_PIN)  # Inicializar sensor MQ135
yl_sensor = ADC(YL_PIN)  # Inicializar sensor de ambiente (YL-100)
pump = PWM(PUMP_PIN, PUMP_FREQ)  # Inicializar bomba
fan = PWM(FAN_PIN, FAN_FREQ)  # Inicializar ventilador
strip = Neopixel(NUMPIXELS, 0, NEO_PIN, "GRB")  # Inicializar strip de LEDs
strip.brightness(100)  # Inicializar brillo del strip de LEDs

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
    try:
        temperature, humidity = dht_sensor.read()
    except Exception as e:
        print(f"Error reading DHT22: {e}")
        temperature = 20
        humidity = 70
    # Read MQ135 sensor (air quality)
    mq_value = mq_sensor.read_u16()
    ppm = (mq_value / 65535) * 3.3
    # Read YL-100 sensor (soil moisture)
    yl_value = yl_sensor.read_u16()
    ground = (yl_value / 65535) * 3.3

# Función para controlar la bomba de agua
def write_pump():
    global ppm, ground
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
    global temperature
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
    read_sensors()  # Read initial sensor values
    while True:
        update_led_strip(RED, PURPLE)  # Update the LED strip with the current colors
        write_fan() # Control the fan based on temperature and humidity
        write_pump() # Control the pump based on ppm and ground
        time.sleep(33)  # Keep the program running
        gc.collect()    # Collect garbage to free up memory
        read_sensors()
        print(f"\nMemoria libre: {gc.mem_free()} bytes") # Print free memory

main_loop()  # Start the main loop