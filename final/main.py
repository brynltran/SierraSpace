import socket
import select
import subprocess
import multiprocessing
import sys
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
# Set up the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server (adjust 'hostname' and 'port')
try:
    sock.connect(('192.168.1.2', 1313))
except socket.error as e:
    print(f"Error connecting to socket: {e}")
    sock.close()
    sys.exit(1)

sock.setblocking(0)

# Dictionary to hold active processes
processes = {}

def start_process(name, command):
    if name not in processes:
        print(f"Starting {name}...")
        processes[name] = subprocess.Popen('sleep 2; echo "Hello"', shell=True, stdout= subprocess.PIPE)
        output = process[name].communicate()[0]
        print(output.decode())
        
    else:
        print(f"{name} is already running.")

def stop_process(name):
    if name in processes:
        print(f"Stopping {name}...")
        processes[name].terminate()
        processes[name].wait()
        del processes[name]

def start_solenoid():
    GPIO.setup(14, GPIO.OUT)
    GPIO.output(14, GPIO.HIGH)
    time.sleep(4.5)
    GPIO.output(14, GPIO.LOW)

def start_burn():
    GPIO.setup(4, GPIO.OUT)
    GPIO.output(4, GPIO.HIGH)
    time.sleep(4.5)
    GPIO.output(4, GPIO.LOW)

def extend():
    GPIO.setup(25, GPIO.OUT)
    GPIO.setup(8, GPIO.OUT)
    GPIO.output(25, GPIO.HIGH)
    GPIO.output(8, GPIO.HIGH)
    time.sleep(2.5)
    GPIO.output(25, GPIO.LOW)

def retract():
    GPIO.setup(25, GPIO.OUT)
    GPIO.setup(8, GPIO.OUT)
    GPIO.output(25, GPIO.HIGH)
    GPIO.output(8, GPIO.LOW)
    time.sleep(6)
    GPIO.output(25, GPIO.LOW)
def unwind():
    DIR_PIN = 21
    STEP_PIN = 18
    STEPS_PER_REVOLUTION = 200
    RPM_MAX = 1000  # 

    GPIO.setup(STEP_PIN, GPIO.OUT)
    GPIO.setup(DIR_PIN, GPIO.OUT)

    GPIO.output(DIR_PIN, GPIO.LOW)  # Set direction to wind

    rpm_unwind = 100  # Set 
    steps_per_second_unwind = rpm_unwind * STEPS_PER_REVOLUTION / 60
    step_interval_unwind = 1 / steps_per_second_unwind
    last_step_time = time.time() - step_interval_unwind
    start = time.time()
    print("HERE!!!!!!!")
    elapsed = 0
    while elapsed < 0.2:
        current_time = time.time()
        if current_time - last_step_time >= step_interval_unwind:
            GPIO.output(STEP_PIN, GPIO.HIGH)
            time.sleep(0.0001)  # Pulse width for the step signal
            GPIO.output(STEP_PIN, GPIO.LOW)
            last_step_time = current_time
        elapsed = time.time() - start
    print("Ending Function Here")
    GPIO.output(DIR_PIN, GPIO.LOW)  # Set direction to wind
    GPIO.output(STEP_PIN, GPIO.LOW)  # Set direction to wind


def wind():
    DIR_PIN = 21
    STEP_PIN = 18
    STEPS_PER_REVOLUTION = 200
    RPM_MAX = 1000  # 

    GPIO.setup(STEP_PIN, GPIO.OUT)
    GPIO.setup(DIR_PIN, GPIO.OUT)

    GPIO.output(DIR_PIN, GPIO.HIGH)  # Set direction to wind

    rpm_unwind = 100  # Set 
    steps_per_second_unwind = rpm_unwind * STEPS_PER_REVOLUTION / 60
    step_interval_unwind = 1 / steps_per_second_unwind
    last_step_time = time.time() - step_interval_unwind
    start = time.time()
    print("HERE!!!!!!!")
    elapsed = 0
    while elapsed < 0.2:
        current_time = time.time()
        if current_time - last_step_time >= step_interval_unwind:
            GPIO.output(STEP_PIN, GPIO.HIGH)
            time.sleep(0.0001)  # Pulse width for the step signal
            GPIO.output(STEP_PIN, GPIO.LOW)
            last_step_time = current_time
        elapsed = time.time() - start
    print("Ending Function Here")
    GPIO.output(DIR_PIN, GPIO.LOW)  # Set direction to wind
    GPIO.output(STEP_PIN, GPIO.LOW)  # Set direction to wind


try:
    current_command = None
    while True:
        ready_to_read, _, _ = select.select([sock], [], [], 0.1)
        if ready_to_read != []:
            #print(ready_to_read)
            data = sock.recv(1024).decode().strip()
            if data:
                print(f"Received command: {data}")
                # Manage multiple actions
                actions = ["burn", "linA", "solenoid", "pid", "unwind"]
                if data == "solenoid":
                    start_solenoid()
                elif data == "burn":
                    start_burn()
                elif data == 'up':
                    extend()
                elif data == 'down':
                    retract()
                elif data == 'pid':
                    print("Got Here")
                    wind()
                    '''
                    stop_event = multiprocessing.Event()
                    p = multiprocessing.Process(target=wind, args=(stop_event,))
                    p.start()
                    while True:
                        data = sock.recv(1024).decode().strip()
                        if data == "off" or data == "pid" or data == "burn" or data =="solenoid" or data == "up" or data == "down":
                            stop_event.set()
                            break
                    print("Stopping PID")
                    p.join()
                    '''
                elif data == 'unwind':
                    unwind()
                    '''
                    stop_event = multiprocessing.Event()
                    p = multiprocessing.Process(target=unwind, args=(stop_event,))
                    p.start()
                    while True:
                        data = sock.recv(1024).decode().strip()
                        if data == "off" or data == "pid" or data == "burn" or data =="solenoid" or data == "up" or data == "down":
                            stop_event.set()
                            break
                    print("Stopping PID")
                    p.join()
                    '''

                #if data in actions: 
                #if data in actions:
                #    if current_command != data:
                #        if current_command:
                #            stop_process(current_command)
                #        start_process(data, ["/path/to/command_for_" + data.replace(" ", "_")])
                #        current_command = data
            else:
                print("No data received, checking if processes need to be stopped...")
                #time.sleep(0.1)
                if current_command:
                    stop_process(current_command)
                    current_command = None
        else:
            pass
            # No new command received, continue with the existing process
            #print(ready_to_read)
            #print("No new command received, continuing existing processes...")
            #time.sleep(0.5)  # Small delay to reduce CPU usage

except KeyboardInterrupt:
    print("Program interrupted by user.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Stop any processes still running
    for name in list(processes):
        stop_process(name)
    sock.close()
    GPIO.cleanup()
    print("Cleanup complete.")

print("Program terminated.")

