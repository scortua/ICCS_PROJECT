import serial, time, random, json, requests
import MySQLdb

db = MySQLdb.connect(host="localhost", 
                     user="RPI4",
                     passwd="raspberry4",
                     db="Invernadero") # Conectar a la base de datos

cursor = db.cursor() # Crear un cursor

uart0 = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)

#url = 'https://api.openweathermap.org/data/2.5/weather?q=Bogota,CO&units=metric&appid=69285e08908ba2461be431c348d1e02d'
#response = requests.get(url)
#datos = response.json()

# leds
led = 'off'
# bomba agua
pump = 'off'

def verificar_(amb):
    if amb == 0:
        amb = 500
    co2 = amb * 10.57
    n = amb * 0.1
    return n,co2,amb

while True:
    try:
        msg = lora.receive()
        msg_json = json.loads(msg)
        data = msg_json['data']
        # Split data string by commas and extract values
        values = data.split(',')
        if len(values) >= 6:  # Ensure we have at least 6 values
            temp = float(values[0])
            hum = float(values[1])
            amb = int(values[2])
            dirt = int(values[3])
            led = values[4]
            pump = values[5]
            # Process ambiente value
            n, co2, amb = verificar_(amb)
            # Print extracted values
            print(f"Temp: {temp}°C, Hum: {hum}%, Ambiente: {amb}, Tierra: {dirt}, LED: {led}, Bomba: {pump}")
            # Save to database
            cursor.execute('''INSERT INTO DHT22 (time, Temperatura, Humedad) VALUES (NOW(), %s, %s);''', (temp, hum))
            cursor.execute('''INSERT INTO MQ_135 (time, CO2, N) VALUES (NOW(), %s, %s);''', (co2, n))
            cursor.execute('''INSERT INTO YL (time, Percentage) VALUES (NOW(), %s);''', (dirt,))
            cursor.execute('''INSERT INTO LEDS (time, Activation) VALUES (NOW(), %s);''', (led,))
            cursor.execute('''INSERT INTO WATER_PUMP (time, Activation) VALUES (NOW(), %s);''', (pump,))
            db.commit()
            print("Data saved to database ---> Received values\nWaiting for new data...")
        else:
            print("Invalid data format received")
        time.sleep(10)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)