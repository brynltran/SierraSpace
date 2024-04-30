#!/usr/bin/env python
import RPi.GPIO as GPIO

from hx711 import HX711

GPIO.setmode(GPIO.BCM)

hx = HX711(dout_pin=9, pd_sck_pin=11)
print('Taring Scale... Please Wait')
hx.zero(readings=30)






hx.set_scale_ratio(2150)

while True:
    weight = hx.get_weight_mean(readings=2)
    print(weight)
