'''
 *
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2021 Daniel Perron
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
'''

import utime
from machine import Pin

class PicoDHT22:
    def __init__(self, dataPin, powerPin=None, dht11=False):
        self.dataPin = dataPin
        self.powerPin = powerPin
        self.dht11 = dht11
        self.dataPin.init(Pin.IN, Pin.PULL_UP)
        if self.powerPin is not None:
            self.powerPin.init(Pin.OUT)
            self.powerPin.value(0)

    def _send_start_signal(self):
        self.dataPin.init(Pin.OUT)
        self.dataPin.value(0)
        utime.sleep_ms(18)  # Start signal > 18ms
        self.dataPin.value(1)
        utime.sleep_us(30)
        self.dataPin.init(Pin.IN)

    def _check_response(self):
        for _ in range(80):
            if not self.dataPin.value():
                break
            utime.sleep_us(1)
        else:
            return False

        for _ in range(80):
            if self.dataPin.value():
                break
            utime.sleep_us(1)
        else:
            return False

        return True

    def _read_bit(self):
        while not self.dataPin.value():
            pass
        utime.sleep_us(30)
        return self.dataPin.value()

    def _read_byte(self):
        byte = 0
        for _ in range(8):
            byte = (byte << 1) | self._read_bit()
        return byte

    def read(self):
        if self.powerPin is not None:
            self.powerPin.value(1)
            utime.sleep_ms(800)

        self._send_start_signal()

        if not self._check_response():
            return None, None

        data = [self._read_byte() for _ in range(5)]

        if self.powerPin is not None:
            self.powerPin.value(0)

        if (sum(data[:4]) & 0xFF) != data[4]:
            return None, None

        if self.dht11:
            humidity = data[0]
            temperature = data[2]
        else:
            humidity = ((data[0] << 8) + data[1]) / 10.0
            temperature = ((data[2] & 0x7F) << 8 | data[3]) / 10.0
            if data[2] & 0x80:
                temperature = -temperature

        return temperature, humidity

if __name__ == "__main__":
    dht_data = Pin(15, Pin.IN, Pin.PULL_UP)
    dht_sensor = PicoDHT22(dht_data, Pin(14, Pin.OUT), dht11=False)
    while True:
        T, H = dht_sensor.read()
        if T is None:
            print("Sensor error")
        else:
            print(f"{T:.1f}°C  {H:.1f}%")
        utime.sleep(2)
