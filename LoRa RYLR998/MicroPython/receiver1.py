from machine import UART, Pin
import time

uart0 = UART(0, baudrate=115200, tx=Pin(12), rx=Pin(13))

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

def write_txt(name,datos):
    try:
        with open(name, 'w') as f:
            for item in datos:
                f.write(str(item) + ',')
            f.write('\n')  # Add a newline at the end of the line
        print(f"Data written to {name}")
    except OSError as e:
        print(f"Error writing to file: {e}")

print("\nConfigurando parametro antena LoRa\n")
time.sleep(0.5)
send_ms("AT") #verificar estado de comandos
time.sleep(1) 
send_ms("AT+RESET") #resetea valores de lora
time.sleep(1)
send_ms("AT+IPR?") #verificacion baudrate
time.sleep(1)
send_ms("AT+ADDRESS=2") #colocar direccion lora 0 - 65535
time.sleep(1)
send_ms("AT+NETWORKID=5") #colocando direccion de red
time.sleep(1)
send_ms("AT+BAND=915000000") #RF frecuency
time.sleep(1)
send_ms("AT+PARAMETER=9,7,1,12") #RF parameters
time.sleep(1)
send_ms("AT+CRFOP?") #RF output power
time.sleep(1)
send_ms("AT+MODE?") #operation mode
time.sleep(1)
send_ms("AT+CPIN?") #contraseña
time.sleep(1)

while True:
    rxData = bytes()
    while uart0.any()>0:
        rxData += uart0.read(1)
    msg = rxData.decode('utf-8')
    print(msg)
    new_msg = msg.replace('+RCV=', '')
    datos = new_msg.split(',')
    # Verifica si se recibieron suficientes datos
    if len(datos) >= VarInMs: 
        id = datos[0]
        data_len = datos[1]
        temp = datos[2]
        hum = datos[3]
        rssi = datos[4]
        snr = datos[5]
        print(f"ID: {id}, Data Len: {data_len}, Data0: {temp}, Data1: {hum}, RSSI: {rssi}, SNR: {snr}")
    
        data_list = [id, data_len, temp, hum, rssi, snr] # Crear una lista con los datos
        write_txt("datos.txt", data_list) # Escribir los datos en el archivo
    else:
        print(f"Error: {datos} \t ({len(datos)}) de ({VarInMs})")
   
    time.sleep(0.5)