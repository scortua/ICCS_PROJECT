import serial, time

uart0 = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)

VarInMs = 6 #variables recibidas en el mensaje
CommasInMs = VarInMs - 1 #comas en el mensaje

def send_ms(ms):
    uart0.write((ms + "\r\n").encode())
    print(ms)
    time.sleep(0.1)
    rec = bytes()
    while uart0.in_waiting>0:
        rec += uart0.read(1)
    print(rec.decode('utf-8'))
    time.sleep(0.1)

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
    while uart0.in_waiting>0:
        rxData += uart0.read(1)
    msg = rxData.decode('utf-8')
    print('\n' + msg)
    new_msg = msg.replace('+RCV=', '')
    dats = new_msg.split(",")

    if len(dats) == VarInMs:
        id = dats[0]
        dat_len = dats[1]
        temp = dats[2]
        hum = dats[3]
        rssi = dats[4]
        snr = dats[5]
        print(f"ID: {id}, Data Length: {dat_len}, Temp: {temp}, Hum: {hum}, RSSI: {rssi}, SNR: {snr}")

        data_list = [id, dat_len, temp, hum, rssi, snr]
        write_txt("data.txt", data_list)
    else:
        print("Not enough data received")

    time.sleep(0.75)


