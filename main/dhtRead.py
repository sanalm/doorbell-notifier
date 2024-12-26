from time import sleep
from machine import Pin
from dht import DHT22
import ujson
import machine
import umail
import urequests
import ubinascii
import urandom as random
import ntptime 
import time
from machine import RTC

class DHTReader:
    def __init__(self):
        self.sensor = DHT22(Pin(15, Pin.IN, Pin.PULL_UP))   # DHT-22 on GPIO 15 (input with internal pull-up resistor)
        self.blueLed = machine.Pin(2, machine.Pin.OUT)
        self.ledInterval = 0.01
        self.readingInterval = 0.5
        self.bellPress = 0
        ntptime.settime()  # Synchronise the system time using NTP
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
            self.send_mail()         

    def init_mail(self, email, attachment = None):
        self.email = email
        self.attachment = attachment

    def boundary(self):
        return ''.join(random.choice('0123456789ABCDEFGHIJKLMNOUPQRSTUWVXYZ') for i in range(15))

    def send_mail(self):
        self.bellPress += 1
        (year, month, mday, week_of_year, hour, minute, second, milisecond)=RTC().datetime()
        RTC().init((year, month, mday, week_of_year, hour+1, minute, second, milisecond)) # GMT correction. GMT+1
        time_now = ("{:02d}/{:02d}/{} {:02d}:{:02d}:{:02d}".format(RTC().datetime()[2],RTC().datetime()[1],RTC().datetime()[0],RTC().datetime()[4],RTC().datetime()[5],RTC().datetime()[6]))
        bell_press_detail = "Bell Press # {0}, {1}\n".format(self.bellPress, time_now)

        capture = False    
        if self.attachment:
            img_buffer = urequests.get(self.attachment['image_capture'])
            if img_buffer.status_code == 200:
                b64 = ubinascii.b2a_base64(img_buffer.content)
                image_html = '<div dir="ltr"><img src="cid:ii_image" alt="drive.jpeg" width="392" height="294"><br></div>'
                capture = True

        smtp = umail.SMTP('smtp.gmail.com', 587, username=self.email['from_email'], password=self.email['from_password'])
        smtp.to(self.email['to'])
        smtp.write("From: ({0})\n".format(self.email['from']))
        smtp.write("To: {0} <{0}>\n".format(self.email['to']))
        smtp.write("Subject: {0}\n".format(self.email['subject']))
        if capture:
            text_id = self.boundary()
            attachment_id = self.boundary()
            smtp.write("MIME-Version: 1.0\n")
            smtp.write('Content-Type: multipart/mixed;\n boundary="------------{0}"\n'.format(attachment_id))
            smtp.write('--------------{0}\nContent-Type: multipart/alternative;\n boundary="------------{1}"\n\n'.format(attachment_id, text_id))
            # smtp.write('--------------{0}\nContent-Type: text/plain; charset=utf-8; format=flowed\nContent-Transfer-Encoding: 7bit\n\n{1}\n\n--------------{0}--\n\n'.format(text_id, bell_press))
            smtp.write('--------------{0}\nContent-Type: text/html; charset=utf-8;\n\n{1}\n\n{2}\n\n--------------{0}--\n\n'.format(text_id, bell_press_detail, image_html))
            smtp.write('--------------{0}\nContent-Type: image/jpeg;\n name="{1}"\nContent-Transfer-Encoding: base64\nX-Attachment-Id: ii_image\nContent-ID: <ii_image>\nContent-Disposition: attachment;\n  filename="{1}"\n\n'.format(attachment_id, self.attachment['name']))
            smtp.write(b64)
            smtp.write('--------------{0}--'.format(attachment_id))
            smtp.send()
        else:
            smtp.send("{} image couldn\'t be retreived\n".format(bell_press))
        smtp.quit()

    def using_email(self, from_email, from_password):
        self.smtp = umail.SMTP('smtp.gmail.com', 587, username=from_email, password=from_password)

    def send_email2(self, to_email, email_body, override_mail_from, email_subject, t):
        self.smtp.to(to_email)
        img_buffer = urequests.get('http://192.168.0.4/img/snapshot.cgi?size=4')
        buffer = "data: \n html: \n <img src={}>\n".format(img_buffer)
        self.smtp.write(buffer)
        email_message = "From: ({})\n".format(override_mail_from)
        email_message += "Subject: {}\n".format(email_subject)
        email_message += " {}C.\n".format(t)
        self.smtp.send(email_message)
        self.smtp.quit()

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