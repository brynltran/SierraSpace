from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(26, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.output(19, True)
while True:

    sleep(1)

    GPIO.output(26, True)
    sleep(1)
    print("working")
    GPIO.output(26, False)

