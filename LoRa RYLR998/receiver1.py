from machine import UART, Pin
import time

uart0 = UART(0, baudrate=115200, tx=Pin(12), rx=Pin(13))

VarInMs = 7 #variables recibidas en el mensaje
CommasInMs = VarInMs - 1 #comas en el mensaje

def send_ms(ms):
    uart0.write(ms + "\r\n") #mandar mensaje
    print(ms) #imprimir mensaje
    time.sleep(0.5)
    rec = bytes()
    rec_ms = False
    while uart0.any()>0:
        rec += uart0.read(1) #recibe datos por uart como char y los concatena
        rec_ms = True
    if rec_ms == True:
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
time.sleep(1)
send_ms("AT") #verificar estado de comandos
time.sleep(0.1) 
send_ms("AT+RESET") #resetea valores de lora
time.sleep(0.1)
send_ms("AT+IPR?") #verificacion baudrate
time.sleep(1)
send_ms("AT+ADDRESS=32323") #colocar direccion lora 0 - 65535
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
    rxData = bytes()
    while uart0.any()>0:
        rxData += uart0.read(1)
    msg = rxData.decode('utf-8')
    print('\n' + msg)
    new_msg = msg.replace('+RCV=', '')
    datos = new_msg.split(',')

    # Verifica si se recibieron suficientes datos
    if len(datos) >= VarInMs: 
        id = datos[0]
        data_len = datos[1]
        data0 = datos[2]
        data1 = datos[3]
        data2 = datos[4]
        rssi = datos[5]
        snr = datos[6]
        print(f"ID: {id}, Data Len: {data_len}, Data0: {data0}, Data1: {data1}, Data2: {data2}, RSSI: {rssi}, SNR: {snr}")
    
        data_list = [id, data_len, data0, data1, data2, rssi, snr] # Crear una lista con los datos
        write_txt("datos.txt", data_list) # Escribir los datos en el archivo
    else:
        print(f"Error: Número de datos recibidos ({len(datos)}) no coincide con lo esperado ({VarInMs})")
   
    time.sleep(5)