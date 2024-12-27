from main.config import Config
from main.ota_updater import OTAUpdater
from main.dhtRead import DHTReader
import os
import machine
from lib.umqttsimple import MQTTClient
import ubinascii
import time

# load configuration for a file
config = Config('main.conf')
ssid = config.get('ssid')
password = config.get('password')
mqtt_server = config.get('mqtt_server')
mqtt_user = config.get('mqtt_user')
mqtt_pass = config.get('mqtt_pass')

def check_for_update_to_install_during_next_reboot():
    o = OTAUpdater('https://github.com/sanalm/doorbell-notifier')
    o.using_network(ssid, password)
    o.check_for_update_to_install_during_next_reboot()

def download_and_install_update_if_available():
    o = OTAUpdater('https://github.com/sanalm/doorbell-notifier')
    o.using_network(ssid, password)
    o.download_and_install_update_if_available(ssid, password)

def start():
    # your custom code goes here. Something like this: ...
    # from main.x import YourProject
    # project = YourProject()
    # ...
    r = DHTReader()
    t = r.measure()
    # r.read_forever()
    r.wait_bell_press()

def boot():
    # if 'next' in os.listdir():
    #     download_and_install_update_if_available()
    # else:
    #     check_for_update_to_install_during_next_reboot()
    start()

# ------------------------------------------------------------------------------------------
# mqtt defs
# ------------------------------------------------------------------------------------------

def sub_cb(topic, msg):
  print((topic, msg))
  if topic == b'notification' and msg == b'received':
    print('ESP received hello message')

def connect_and_subscribe():
  client_id = ubinascii.hexlify(machine.unique_id())
  topic_sub = b'notification'

  client = MQTTClient(client_id, mqtt_server, user=mqtt_user, password=mqtt_pass)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

last_message = 0
message_interval = 5
counter = 0
topic_pub = b'hello'

while True:
  try:
    client.check_msg()
    if (time.time() - last_message) > message_interval:
      msg = b'Hello #%d' % counter
      client.publish(topic_pub, msg)
      last_message = time.time()
      counter += 1
  except OSError as e:
    restart_and_reconnect()

#
# ------------------------------------------------------------------------------------------
#

boot()
