#!/usr/bin/env python
import RPi.GPIO as GPIO
from hx711 import HX711
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Set Up and Tare
GPIO.setmode(GPIO.BCM)
hx = HX711(dout_pin=9, pd_sck_pin=11)
print('Taring Scale... Please Wait')
hx.zero(readings=10)
hx.set_scale_ratio(2150)  #2150 was tested as the best ratio 

# Initialize Lists to store elapsed time (in seconds) and sensor values (in grams)
elapsed_times = []
values = []

# Capture the start time
start_time = time.time()

fig, ax = plt.subplots()
line, = ax.plot(elapsed_times, values, '-')

def init():
    ax.set_xlim([0, 15])  # Show last 15 seconds of data
    ax.set_ylim([0, 500])  # Adjusted to 500 as that is ~upper limit of load cell
    return line,

def update(frame):
    # Calculate elapsed time since start
    current_time = time.time() - start_time
    elapsed_times.append(current_time)
    value = hx.get_weight_mean(readings=1)
    print(value)
    values.append(value)

    # Keep data within the last 15 seconds
    while elapsed_times and elapsed_times[0] < current_time - 15:
        elapsed_times.pop(0)
        values.pop(0)

    line.set_data(elapsed_times, values)
    ax.set_xlim([max(0, current_time - 15), max(15, current_time)])
    ax.relim()
    ax.autoscale_view()
    return line,

ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=1000)

# Set labels (optional)
ax.set_xlabel('Elapsed Time (seconds)')
ax.set_ylabel('Weight (grams)')

plt.show()

# Cleanup GPIO when done
GPIO.cleanup()
