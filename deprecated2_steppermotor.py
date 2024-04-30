import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
import time


direction = 14
step = 12
EN_pin = 15

mymotortest = RpiMotorLib.A4988Nema(direction, step, (21,21,21), "DRV8825")
GPIO.setup(EN_pin, GPIO.OUT)

GPIO.output(EN_pin,GPIO.LOW)
while True:
    mymotortest.motor_go(False,
        "Full",
        400,
        0.0005,
        False,
        0.5)

GPIO.cleanup()
