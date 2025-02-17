from machine import UART, Pin
import time

uart0 = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

# +RVC= address, len, temp, hum, rssi, snr
VarInMs = 6 #variables recibidas en el mensaje
CommasInMs = VarInMs - 1 #comas en el mensaje

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
    send_ms("AT") #verificar estado de comandos
    time.sleep(1) 
    send_ms("AT+ADDRESS=2") #colocar direccion lora 0 - 65535
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
while True:
    rxData = bytes()
    while uart0.any()>0:
        rxData += uart0.read(1)
    msg = rxData.decode('utf-8')
    print(msg)
    new_msg = msg.replace('+RCV=', '')
    datos = new_msg.split(',')
    # Verifica si se recibieron suficientes datos
    if len(datos) == VarInMs: 
        print(datos)
    else:
        print(f"Error: {datos} \t ({len(datos)}) de ({VarInMs})")
   
    time.sleep(7)


