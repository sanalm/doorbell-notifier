from main.config import Config
import time
from lib.umqttsimple import MQTTClient
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

# load configuration for a file
config = Config('main.conf')
ssid = config.get('ssid')
password = config.get('password')
mqtt_server = config.get('mqtt_server')
mqtt_user = config.get('mqtt_user')
mqtt_pass = config.get('mqtt_pass')

last_message = 0
message_interval = 5
counter = 0

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

import main.main