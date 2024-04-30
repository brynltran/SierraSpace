import RPi.GPIO as GPIO
import time

INHA = 20
INHB = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(INHA, GPIO.OUT)
GPIO.setup(INHB, GPIO.OUT)
GPIO.output(INHA, GPIO.LOW)
GPIO.output(INHB, GPIO.LOW)
def extend():
    GPIO.output(INHA, GPIO.LOW)
    GPIO.output(INHB, GPIO.HIGH)

def retract():
   GPIO.output(INHA, GPIO.HIGH)
   GPIO.output(INHB, GPIO.LOW)

def stop():
   GPIO.output(INHA, GPIO.LOW)
   GPIO.output(INHB, GPIO.LOW)

try:
    while True:
        extend()
        time.sleep(3)
        retract()
        time.sleep(3)
except KeyboardInterrupt:
    stop()

finally:
    GPIO.cleanup()
