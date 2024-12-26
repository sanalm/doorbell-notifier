# doorbell-notifier
This repository contains ESP32 micropython firmware to subcribe to the door bell over MQTT and send a whatsapp message from the ESP32 dev board
It can also send the door bell notification by email and carry out OTA upgrade

ESP32 steps:

1. Subscribe to topic: home/bedroom/boxroom/temperature/req {"read":"temperature"}
2. On receiving topic, publish: home/bedroom/boxroom/temperature/cnf {"temperature":2100}
3. Subscribe to topic: home/doorbell/ind with contents
{
  "bellPush": {
    "count": 1,
    "time": 1735210160
  }
}

## Raspberry Pi

rshell --buffer-size=30 -p /dev/ttyUSB0

### To see what files are written to ESP32 board
ls /pyboard

e.g. 

/home/pi/workspace/micropython_vs/temperature-logger> ls /pyboard

main/               umail.py            pymakr.conf        
boot.py             main.conf           door.code-workspace

### To write from Raspberry Pi to ESP32
cp main/dhtRead.py /pyboard/main/dhtRead.py

### Flash Python environment

Whilst pressing the "Boot" button on the esp32

  `ls ~/Downloads/esp32-20210902-v1.17.bin`

  `sudo esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 ~/Downloads/esp32-20210902-v1.17.bin` 

Release button when flashing starts

## Serial port
   `sudo minicom --baudrate 115200 --device /dev/ttyUSB0`
