import RPi.GPIO as GPIO

from hx711 import HX711

GPIO.setmode(GPIO.BCM)

hx = HX711(dout_pin=9, pd_sck_pin=11)
print('Taring Scale... Please Wait')
hx.zero(readings=80)


input('place known weight, then press enter: ')

reading = hx.get_data_mean(readings=99)

known_weight_grams = input('Enter known weight in grams,then press enter: ')

value = float(known_weight_grams)

ratio = reading/value
print(f'Ratio: {ratio}')
hx.set_scale_ratio(ratio)

while True:
    weight = hx.get_weight_mean()
    print(weight)
