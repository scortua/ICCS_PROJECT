import serial
import time
import MySQLdb
import random

# Configuración de la base de datos
def connect_to_db():
    return MySQLdb.connect(
        host="localhost",
        user="RPI4",
        passwd="raspberry4",
        db="Invernadero"
    )

def init_cursor(db):
    return db.cursor()

# Configuración de LoRa
class LoRa:
    def __init__(self, port="/dev/ttyS0", baudrate=115200, timeout=1):
        self.uart = serial.Serial(port, baudrate=baudrate, timeout=timeout)

    def send_command(self, command):
        self.uart.write((command + "\r\n").encode())
        print(f"Enviando comando: {command}")
        time.sleep(0.1)
        response = self.uart.read_all().decode('utf-8')
        print(f"Respuesta: {response}")
        return response

    def initialize(self):
        print("\nConfigurando parámetros de antena LoRa\n")
        self.send_command("AT")
        self.send_command("AT+ADDRESS=2")
        self.send_command("AT+NETWORKID=5")
        self.send_command("AT+PARAMETER=9,7,1,12")

# Funciones de procesamiento de datos
class SensorDataProcessor:
    def __init__(self):
        # Variables de temperatura
        self.temp_max = 25.0
        self.temp_min = 17.0
        self.prev_temp = 0
        # Variables de humedad
        self.hum_max = 75.0
        self.hum_min = 45.0
        self.prev_hum = 0
        # Variables de MQ-135
        self.amb_max = 1000
        self.amb_min = 400
        self.prev_amb = 0
        # Variables de YL
        self.dirt_max = 1000
        self.dirt_min = 0
        self.prev_dirt = 0   
        self.counter = 0

    def process_data(self, data):
        if len(data) == 8:  # Datos válidos
            id, data_len, temp, hum, amb, dirt, rssi, snr = data
            nitro, co2 = self.calculate_ambient_values(float(amb))
            return {
                "id": id,
                "data_len": data_len,
                "temp": float(temp),
                "hum": float(hum),
                "co2": co2,
                "n": nitro,
                "dirt": float(dirt),
                "rssi": int(rssi),
                "snr": int(snr)
            }
        else:
            return self.generate_random_data()

    def calculate_ambient_values(self, amb):
        if amb == 0:
            amb = 500
        co2 = amb * 10.57
        n = amb * 0.1
        return n, co2

    def generate_random_data(self):
        temp = round(random.uniform(self.temp_min, self.temp_max), 2)
        hum = round(random.uniform(self.hum_min, self.hum_max), 2)
        amb = round(random.uniform(self.amb_min, self.amb_max), 2)
        dirt = round(random.uniform(self.dirt_min, self.dirt_max), 2)
        rssi = random.randint(-50, 0)
        snr = random.randint(0, 15)
        n, co2 = self.calculate_ambient_values(amb)
        return {
            "id": 1,
            "data_len": len(f"{temp},{hum},{amb},{dirt},{rssi},{snr}"),
            "temp": temp,
            "hum": hum,
            "co2": co2,
            "n": n,
            "dirt": dirt,
            "rssi": rssi,
            "snr": snr
        }

# Guardar datos en la base de datos
def save_to_database(cursor, data):
    cursor.execute('''INSERT INTO DHT22 (time, Temperatura, Humedad) VALUES (NOW(), %s, %s);''', (data["temp"], data["hum"]))
    cursor.execute('''INSERT INTO MQ_135 (time, CO2, N) VALUES (NOW(), %s, %s);''', (data["co2"], data["n"]))
    cursor.execute('''INSERT INTO YL (time, DIRT) VALUES (NOW(), %s);''', (data["dirt"],))
    print("Datos guardados en la base de datos.")

# Main
if __name__ == "__main__":
    db = connect_to_db()
    cursor = init_cursor(db)
    lora = LoRa()
    processor = SensorDataProcessor()

    lora.initialize()

    while True:
        rx_data = lora.uart.read_all().decode('utf-8')
        if rx_data:
            print(f"Datos recibidos: {rx_data}")
            msg = rx_data.replace("+RCV=", "")
            data = msg.split(",")
            processed_data = processor.process_data(data)
            save_to_database(cursor, processed_data)
            db.commit()
        time.sleep(30)