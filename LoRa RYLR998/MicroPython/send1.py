from machine import UART, Pin, I2C
import time, random, ssd1306

i2c = I2C(1,scl=Pin(15), sda=Pin(14))
uart0 = UART(0, baudrate=115200, tx=Pin(12), rx=Pin(13)) #inicializar uart0
led = Pin(25, Pin.OUT) #prueba funcionamiento con led

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c, addr=0x3C)

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
    
    oled.fill(0)
    oled.text('AT+SEND=32323,',0,20)
    oled.text(data_len + ',' + data,0,30)
    oled.show()
    
    led.value(1)
    time.sleep(1)
    led.value(0)
    time.sleep(1)