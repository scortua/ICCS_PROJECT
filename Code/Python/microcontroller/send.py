from machine import UART, Pin
import time, random
from PicoDHT22 import PicoDHT22
from reyax import ReyaxLoRa   # Properly import and use the reyax library

# Initialize UART for LoRa module
uart0 = UART(0, baudrate=115200, tx=Pin(12), rx=Pin(13))
dht = PicoDHT22(Pin(14, Pin.IN, Pin.PULL_UP))
led = Pin(25, Pin.OUT)

# Create LoRa module instance
lora = ReyaxLoRa(uart0)

def init_lora():
    print("\nConfigurando parametro antena LoRa\n")
    time.sleep(2)
    
    # Configure LoRa parameters using the library
    print(lora.test_at())  # AT command to check if module responds
    print(lora.set_address(1))  # Set address (1)
    print(lora.set_network_id(5))  # Set network ID (5)
    print(lora.set_band(915000000))  # RF frequency (915MHz)
    print(lora.set_parameters(9, 7, 1, 12))  # Set RF parameters
    print(lora.get_mode())  # Get operation mode
    print(lora.get_cpin())  # Get password status

# Initialize LoRa
init_lora()
time.sleep(1)

while True:
    # Read temperature and humidity (or generate random values)
    try:
        T, H = dht.read()
    except:
        # Fallback to random values if sensor read fails
        T = random.randint(0, 100)
        H = random.randint(0, 100)
    
    data = f"{T},{H}"  # Format data as string
    print(f'T={T}°C H={H}')
    
    # Send data using the reyax library
    result = lora.send_data(2, data)  # Send to address 2
    print(f"Send result: {result}")
    
    # Blink LED to indicate transmission
    led.value(1)
    time.sleep(10)
    led.value(0)
