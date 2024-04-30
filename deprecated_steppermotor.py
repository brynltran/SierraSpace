from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.OUT)
while True:


    GPIO.output(18, True)
    print("working")
    GPIO.output(18, False)

