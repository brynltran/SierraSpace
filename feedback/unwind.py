import RPi.GPIO as GPIO
from time import sleep, time

GPIO.setmode(GPIO.BCM)

DIR_PIN = 21
STEP_PIN = 18
STEPS_PER_REVOLUTION = 200
RPM_MAX = 620  # 

GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)

GPIO.output(DIR_PIN, GPIO.HIGH)  # Set direction to unwind

rpm_unwind = 100  # Set 
steps_per_second_unwind = rpm_unwind * STEPS_PER_REVOLUTION / 60
step_interval_unwind = 1 / steps_per_second_unwind

last_step_time = time() - step_interval_unwind

try:
    while True:
        current_time = time()
        if current_time - last_step_time >= step_interval_unwind:
            GPIO.output(STEP_PIN, GPIO.HIGH)
            sleep(0.0001)  # Pulse width for the step signal
            GPIO.output(STEP_PIN, GPIO.LOW)
            last_step_time = current_time
except KeyboardInterrupt:
    GPIO.cleanup()
