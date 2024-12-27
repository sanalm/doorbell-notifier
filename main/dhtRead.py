from time import sleep
from machine import Pin
from dht import DHT22
import ujson
import machine
import time
from machine import RTC
from lib.umqttsimple import MQTTClient

class DHTReader:
    def __init__(self):
        self.sensor = DHT22(Pin(15, Pin.IN, Pin.PULL_UP))   # DHT-22 on GPIO 15 (input with internal pull-up resistor)
        self.blueLed = machine.Pin(2, machine.Pin.OUT)
        self.ledInterval = 0.01
        self.readingInterval = 0.5
        self.bellPress = 0
        self.pin_d18 = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_DOWN)

    def wait_pin_change(self, pin):
        # wait for pin to change value
        # it needs to be stable for a continuous 20ms
        cur_value = pin.value()
        active = 0
        while active < 20:
            if pin.value() != cur_value:
                active += 1
            else:
                active = 0
            time.sleep_ms(1)

    def wait_bell_press(self):
        while True:
            self.wait_pin_change(self.pin_d18)
            self.blueLed.value(1)
            sleep(self.ledInterval)
            self.blueLed.value(0)
            self.measure()

    def measure(self):
        try:
            self.sensor.measure()   # Poll sensor
            t = self.sensor.temperature()
            h = self.sensor.humidity()
            if isinstance(t, float) and isinstance(h, float):  # Confirm sensor results are numeric
                reading = {}
                reading["temperature"] = t
                reading["humidity"] = h
                reading["interval"] = self.readingInterval
                encodedReading = ujson.dumps(reading)
                print(encodedReading)
                self.blueLed.value(1)
                sleep(self.ledInterval)
                self.blueLed.value(0)
                sleep(self.ledInterval)
                sleep(self.readingInterval)
            else:
                t = 0
                print('Invalid sensor readings.')
        except OSError:
            t = 0
            print('Failed to read sensor.')
        self.blueLed.value(1)
        sleep(self.ledInterval)
        self.blueLed.value(0)
        sleep(self.ledInterval)
        sleep(self.readingInterval)
        return t

    def read_forever(self):
        while True:
            t = self.measure()