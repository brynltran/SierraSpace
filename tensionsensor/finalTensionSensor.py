import RPi.GPIO as GPIO
from hx711 import HX711

GPIO.setmode(GPIO.BCM)                 # set GPIO pin mode to BCM numbering
hx = HX711(dout_pin=9, pd_sck_pin=11)

hx.zero(readings=50)
while True:
    reading = hx.get_data_mean()
    print(reading)
