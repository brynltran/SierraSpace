import RPi.GPIO as GPIO
import time

data = 25
direction = 8

GPIO.setmode(GPIO.BCM)
GPIO.setup(data, GPIO.OUT)
GPIO.setup(direction, GPIO.OUT)
GPIO.output(data, GPIO.LOW)
GPIO.output(direction, GPIO.LOW)


def retract():
    GPIO.output(data, GPIO.HIGH)
    GPIO.output(direction, GPIO.LOW)

def extend():
   GPIO.output(data, GPIO.HIGH)
   GPIO.output(direction, GPIO.HIGH)

def stop():
   GPIO.output(data, GPIO.LOW)
   GPIO.output(direction, GPIO.LOW)

try:
    while True:
        retract()
        time.sleep(3)
        #retract()
        #time.sleep(3)
except KeyboardInterrupt:
    stop()

finally:
    GPIO.cleanup()
