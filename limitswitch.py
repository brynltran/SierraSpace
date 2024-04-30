from gpiozero import LED, Button 
from time import sleep

switch = Button(17, pull_up=True)
led = LED(4)
button = 17
while True:
    if switch.is_pressed:
        led.off()
    else:
        led.on()
