import threading
import socket
import select
import subprocess
import sys
import time
import RPi.GPIO as GPIO

# Setup GPIO
GPIO.setmode(GPIO.BCM)  # BCM is one of the numbering schemes for GPIO
GPIO.setup(14, GPIO.OUT)

# Event to signal the reception of new data
new_data_event = threading.Event()

def operate_solenoid():
    """Function to operate the solenoid."""
    GPIO.output(14, GPIO.HIGH)  # Turn solenoid on
    time.sleep(5)  # Keep solenoid on for 5 seconds
    GPIO.output(14, GPIO.LOW)  # Turn solenoid off

def timer_thread(timeout=1.0):
    while True:
        if new_data_event.wait(timeout):
            print("New data received, resetting timer...")
            new_data_event.clear()
        else:
            print("Timeout occurred, no new data within the timeout period. Terminating processes...")
            for name in list(processes.keys()):
                stop_process(name)
            break

def start_process(name, command):
    if name not in processes:
        print(f"Starting {name}...")
        if name == "solenoid":
            operate_solenoid()  # Specific function call for the solenoid
        else:
            processes[name] = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            output, _ = processes[name].communicate()
            if output:
                print(output.decode())
    else:
        print(f"{name} is already running.")

def stop_process(name):
    if name in processes:
        print(f"Stopping {name}...")
        processes[name].terminate()
        processes[name].wait()
        del processes[name]

def command_listener():
    try:
        while True:
            ready_to_read, _, _ = select.select([sock], [], [], 0.1)
            if ready_to_read:
                data = sock.recv(1024).decode().strip()
                if data:
                    print(f"Received command: {data}")
                    actions = ["burn", "linA", "solenoid", "pid", "unwind"]
                    if data in actions:
                        print("Valid command received, resetting timer.")
                        new_data_event.set()
                        start_process(data, f'sleep 2; echo "Process for {data}"')
            else:
                print("No new command received, continuing existing processes...")
    except Exception as e:
        print(f"An error occurred in command listener: {e}")

# Network setup
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setblocking(0)
try:
    sock.connect(('192.168.1.2', 1313))
except socket.error as e:
    print(f"Error connecting to socket: {e}")
    sock.close()
    sys.exit(1)

# Threads
timer = threading.Thread(target=timer_thread, args=(1.0,))
listener = threading.Thread(target=command_listener)
timer.start()
listener.start()

try:
    timer.join()
    listener.join()
except KeyboardInterrupt:
    print("Program interrupted by user.")
finally:
    GPIO.cleanup()  # Reset GPIO settings
    sock.close()
    for name in list(processes.keys()):
        stop_process(name)
    print("Cleanup complete.")
print("Program terminated.")

