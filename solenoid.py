from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)

while True:
    sleep(1)

    GPIO.output(21, True)
    sleep(1)
    print("working")
    GPIO.output(21, False)

