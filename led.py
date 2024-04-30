from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(2, GPIO.OUT)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)
while True:
    GPIO.output(2, True)
    sleep(1)
    GPIO.output(2, False)
    GPIO.output(3, True)
    sleep(1)
    GPIO.output(3, False)
    GPIO.output(4, True)
    sleep(1)
    GPIO.output(4, False)

