import serial, time
import MySQLdb
import random

db = MySQLdb.connect(host="localhost", 
                     user="RPI4",
                     passwd="raspberry4",
                     db="Invernadero") # Conectar a la base de datos

cursor = db.cursor() # Crear un cursor

uart0 = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)

VarInMs = 7 #variables recibidas en el mensaje
CommasInMs = VarInMs - 1 #comas en el mensaje
temp_max = 25.0
temp_min = 17.0
hum_max = 75.0
hum_min = 45.0
amb_max = 1000
amb_min = 400
ambient = 0
counter = 0
prev_temp = 0
prev_hum = 0
prev_amb = 0

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

def verificar_():
    if amb == 0:
        amb = 500
    co2 = amb * 10.57
    n = amb * 0.1
    return n,co2,amb


init_lora()
while True:
    rxData = bytes()
    while uart0.in_waiting > 0:
        rxData += uart0.read(uart0.in_waiting)
    msg = rxData.decode('utf-8')
    print('\n' + msg)
    new_msg = msg.replace('+RCV=', '')
    data = new_msg.split(",")

    if len(data) == VarInMs:
        id = data[0]
        data_len = data[1]
        temp = data[2]
        hum = data[3]
        amb = data[4]
        n,co2,amb = verificar_()
        rssi = data[5] # Received Signal Strength Indicator
        snr = data[6]  # Signal to Noise Ratio
        print(f"ID: {id}, Data Length: {data_len}, Temp: {temp}, Hum: {hum}, PPM: {amb}, RSSI: {rssi}, SNR: {snr}")
        cursor.execute('''INSERT INTO DHT22 (time,Temperatura, Humedad) VALUES (NOW(),%s, %s);''',(temp,hum))
        db.commit()
        cursor.execute('''INSERT INTO MQ_135 (time,CO2, N) VALUES (NOW(),%s, %s, %s);''',(co2,n))
        db.commit()
        print("Data saved to database ---> Received values\nWaiting for new data...")
        prev_temp = float(temp)
        prev_hum = float(hum)
    else:
        id = 1
        if prev_temp != 0 and prev_hum != 0:
            temp = round(random.uniform(prev_temp - 0.5, prev_temp + 0.5), 2)
            hum = round(random.uniform(prev_hum - 1.5, prev_hum + 1.5), 2)
        else:
            temp = round(random.uniform(temp_min, temp_max), 2)
            hum = round(random.uniform(hum_min, hum_max), 2)
        if prev_amb != 0:
            amb = round(random.uniform(prev_amb - 50, prev_amb + 50), 2)
        else:
            amb = round(random.uniform(amb_min, amb_max), 2)
        n,co2,amb = verificar_()
        # Ensure the new max/min values stay within the initial range
        temp_max = min(temp + 0.5, 25.0)
        temp_min = max(temp - 0.5, 17.0)
        hum_max = min(hum + 1.5, 75.0)
        hum_min = max(hum - 1.5, 45.0)
        amb_max = min(amb + 50, 1000)
        amb_min = max(amb - 50, 400)
        data_len = len(str(temp) + ',' + str(hum) + ',' + str(co2) + ',' + str(n))
        rssi = random.randint(-50, 0)
        snr = random.randint(0, 15)
        # Drastic change after 7 iterations
        if counter <= 7:
            counter += 1
        if counter > 7:
            temp_max = 25.0
            temp_min = 17.0
            hum_max = 75.0
            hum_min = 45.0
            amb_max = 1000
            amb_min = 400
            counter = 0
        print(f"Count:{counter}, ID:{id}, Data Length:{data_len}, Temp:{temp}, Hum:{hum}, RSSI:{rssi}, SNR:{snr}")
        cursor.execute('''INSERT INTO DHT22 (time,Temperatura, Humedad) VALUES (NOW(),%s, %s);''',(temp,hum))
        db.commit()
        cursor.execute('''INSERT INTO MQ_135 (time,CO2, N) VALUES (NOW(),%s, %s, %s);''',(co2,n))
        db.commit()        
        print("Data saved to database ---> Random values\nWaiting for new data...")

    time.sleep(30)