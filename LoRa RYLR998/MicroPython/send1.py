from machine import UART, Pin, I2C
import ssd1306
from PicoDHT22 import PicoDHT22
import time, random

# protocols configs
i2c = I2C(1,scl=Pin(15), sda=Pin(14))
uart0 = UART(0, baudrate=115200, tx=Pin(16), rx=Pin(17)) #inicializar uart0
led = Pin(25, Pin.OUT) #prueba funcionamiento con led
dht = PicoDHT22(Pin(13,Pin.IN,Pin.PULL_UP))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
      
def loading(x):
    oled.text('#',x,40)
    oled.show()
    
def scroll_in_out(display):
    for i in range (0,(oled_width+1)*2,1):
        for line in display:
            oled.text(line[2],-oled_width+i,line[1])
        oled.show()
        if i!=oled_width:
            oled.fill(0)
        
def init_rp():
    muestra=[[0,20,'INICIANDO'],[20,40,'<-O_O->']]
    scroll_in_out(muestra)
    time.sleep(2)
    
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
    time.sleep(0.5)
    loading(12)
    send_ms("AT") #verificar estado de comandos
    time.sleep(1)
    loading(20)
    send_ms("AT+RESET") #resetea valores de lora
    time.sleep(1)
    loading(28)
    send_ms("AT+IPR?") #verificacion baudrate
    time.sleep(1)
    loading(36)
    send_ms("AT+ADDRESS=1") #colocar direccion lora 0 - 65535
    time.sleep(1)
    loading(44)
    send_ms("AT+NETWORKID=5") #colocando direccion de red
    time.sleep(1)
    loading(52)
    send_ms("AT+BAND=915000000") #RF frecuency
    time.sleep(1)
    loading(60)
    send_ms("AT+PARAMETER=9,7,1,12") #RF parameters
    time.sleep(1)
    loading(68)
    send_ms("AT+CRFOP?") #RF output power
    time.sleep(1)
    loading(76)
    send_ms("AT+MODE?") #operation mode
    time.sleep(1)
    loading(84)
    send_ms("AT+CPIN?") #contraseña
    time.sleep(1)
    loading(92)
    
def lcd(message):
    oled.fill(0)
    oled.text(message[0],0,0)
    oled.text('Size: ' + message[1],0,20)
    oled.text('Temp:' + message[2][0:4] + ' `C',0,30) # xx.x°C -> 0:3   4 comma
    oled.text('Hume:' + message[2][5:] + ' %',0,40) # xx.x% -> 5:final
    oled.show()

# Inicializar LoRa
init_rp()
oled.text('Config LoRa',15,20)
oled.show()
init_lora()

while True:
    #value0 = random.randint(-100,100)
    
    # Funcion sensor dht
    #T, H = dht.read()
    T = 20.0
    H = 71.2
    
    data = str(T) + ',' + str(H) #convertir en string
    data_len = str(len(data))
    send_ms('AT+SEND=2,' + data_len + ',' + data) #"AT+SEND=AddressToSent+len_data+data
    ms = ('AT+SEND=2', data_len, data)
    print(f'T={T}°C H={H}')
    
    # Pantalla LCD
    lcd(ms)
    
    led.value(1)
    time.sleep(2.5)
    led.value(0)
    time.sleep(2.5)