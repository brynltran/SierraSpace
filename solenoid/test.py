import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)
GPIO.setup(14, GPIO.OUT)
while True:
    GPIO.output(14, GPIO.HIGH)
    print("high")
