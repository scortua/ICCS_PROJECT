from machine import UART, Pin
import time, random

uart0 = UART(0, baudrate=115200, tx=Pin(12), rx=Pin(13)) #inicializar uart0
led = Pin(25, Pin.OUT) #prueba funcionamiento con led

def send_ms(ms):
    uart0.write(ms + "\r\n") #mandar mensaje
    print(ms) #imprimir mensaje
    time.sleep(0.5)
    rec = bytes()
    while uart0.any()>0:
        rec += uart0.read(1) #recibe datos por uart como char y los concatena
    print(rec.decode('utf-8'))  #Imprime el caracter recibido
        

print("\nConfigurando parametro antena LoRa\n")
time.sleep(1)
send_ms("AT") #verificar estado de comandos
time.sleep(0.1) 
send_ms("AT+RESET") #resetea valores de lora
time.sleep(0.1)
send_ms("AT+IPR?") #verificacion baudrate
time.sleep(1)
send_ms("AT+ADDRESS=32321") #colocar direccion lora 0 - 65535
time.sleep(0.1)
send_ms("AT+NETWORKID=13") #colocando direccion de red
time.sleep(0.1)
send_ms("AT+BAND=915000000") #RF frecuency
time.sleep(0.1)
send_ms("AT+PARAMETER=8,7,1,12") #RF parameters
time.sleep(0.1)
send_ms("AT+CRFOP?") #RF output power
time.sleep(0.1)
send_ms("AT+MODE?") #operation mode
time.sleep(0.1)
send_ms("AT+CPIN?") #contraseña
time.sleep(0.1)
    

while True:
    #value0 = random.randint(-100,100)
    value0 = 1
    value1 = 400
    value2 = -13
    data = str(value0) + ',' + str(value1) + ',' + str(value2) #convertir en string
    data_len = str(len(data))
    send_ms('AT+SEND=32323,' + data_len + ',' + data) #"AT+SEND=AddressToSent+len_data+data
    
    led.value(1)
    time.sleep(1)
    led.value(0)
    time.sleep(1)