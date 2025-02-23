import serial, time
import MySQLdb

db = MySQLdb.connect(host="localhost", 
                     user="RPI4",
                     passwd="raspberry4",
                     db="Invernadero") # Conectar a la base de datos

cursor = db.cursor() # Crear un cursor

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

def init_lora():
    print("\nConfigurando parametro antena LoRa\n")
    time.sleep(0.5)
    send_ms("AT") #verificar estado de comandos
    time.sleep(0.1)
    send_ms("AT+ADDRESS=2") #colocar direccion lora 0 - 65535
    time.sleep(0.1)
    send_ms("AT+NETWORKID=5") #colocando direccion de red
    time.sleep(0.1)
    send_ms("AT+PARAMETER=9,7,1,12") #RF parameters
    time.sleep(0.1)
    send_ms("AT+MODE?") #operation mode
    time.sleep(0.1)
    send_ms("AT+CPIN?") #contraseña
    time.sleep(0.1)


init_lora()
while True:
    rxData = bytes()
    while uart0.in_waiting > 0:
        rxData += uart0.read(uart0.in_waiting)
    if rxData:
        msg = rxData.decode('utf-8')
        print('\n' + msg)
        new_msg = msg.replace('+RCV=', '')
        data = new_msg.split(",")

        if len(data) == VarInMs:
            id = data[0]
            data_len = data[1]
            temp = data[2]
            hum = data[3]
            rssi = data[4]
            snr = data[5]
            print(f"ID: {id}, Data Length: {data_len}, Temp: {temp}, Hum: {hum}, RSSI: {rssi}, SNR: {snr}")
            cursor.execute('''INSERT INTO DHT22 (time,Temperatura, Humedad) VALUES (NOW(),%s, %s);''',(temp,hum))
            db.commit()
            print("Data saved to database")
        else:
            print(f"Error: {data} \t ({len(data)}) de ({VarInMs})")
            print("Data did not saved to database")

    time.sleep(5)