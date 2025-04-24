from machine import UART, Pin
import time, random
from Code.Python.libraries.PicoDHT22 import PicoDHT22   
   
uart0 = UART(0, baudrate=115200, tx=Pin(12), rx=Pin(13)) #inicializar uart0    
dht = PicoDHT22(Pin(14,Pin.IN,Pin.PULL_UP))
led = Pin(25,Pin.OUT)

def send_ms(ms):
    uart0.write(ms + "\r\n") #mandar mensaje
    print(ms) #imprimir mensaje
    time.sleep(0.5)
    rec = bytes()
    while uart0.any()>0:
        rec += uart0.read(1) #recibe datos por uart como char y los concatena
    print(rec.decode('utf-8'))  #Imprime el caracter recibido
    
    
def init_lora():
    print("\nConfigurando parametro antena LoRa\n")
    time.sleep(2)
    send_ms("AT") #verificar estado de comandos
    time.sleep(1)
    send_ms("AT+ADDRESS=1") #colocar direccion lora 0 - 65535
    time.sleep(1)
    send_ms("AT+NETWORKID=5") #colocando direccion de red
    time.sleep(1)
    send_ms("AT+BAND=915000000") #RF frecuency
    time.sleep(1)
    send_ms("AT+PARAMETER=9,7,1,12") #RF parameters
    time.sleep(1)
    send_ms("AT+MODE?") #operation mode
    time.sleep(1)
    send_ms("AT+CPIN?") #contraseña
    time.sleep(1)
    

# Inicializar LoRa
init_lora()
time.sleep(1)
while True:
    #value0 = random.randint(-100,100)
    # Funcion sensor dht
    #T,H = dht.read()
    T = random.randint(0,100)
    H = random.randint(0,100)
    data = str(T) + ',' + str(H) #convertir en string
    data_len = str(len(data))
    print(f'T={T}°C H={H}')
    send_ms('AT+SEND=2,' + data_len + ',' + data) #"AT+SEND=AddressToSent+len_data+t,h
    led.value(1)
    time.sleep(10)
    led.value(0)


