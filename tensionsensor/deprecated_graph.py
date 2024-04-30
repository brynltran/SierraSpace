#!/usr/bin/env python
import RPi.GPIO as GPIO
from hx711 import HX711
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates

#Set Up and Tare
GPIO.setmode(GPIO.BCM)
hx = HX711(dout_pin=9, pd_sck_pin=11)
print('Taring Scale... Please Wait')
hx.zero(readings=10)
hx.set_scale_ratio(2150)
#Initialize Lists to store timestamps and sensor values

times = []
values = []

fig, ax = plt.subplots()
line, = ax.plot_date(times, values, '-')


def init():
    ax.set_xlim([time.time(), time.time() + 10])
    ax.set_ylim([0,100])
    return line,


def update(frame):
    current_time = datetime.now(timezone.utc)  # Ensures timezone awareness
    times.append(current_time)
    value = hx.get_weight(5)
    print(value)
    values.append(value)

    if len(times) > 15:
        times.pop(0)
        values.pop(0)

    line.set_data(times, values)
    ax.set_xlim([times[0], times[-1]])
    ax.relim()
    ax.autoscale_view()
    return line,


ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=1000)

ax.xaxis.set_major_locator(mdates.MinuteLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

plt.show()
