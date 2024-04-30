import threading
import socket
import select
import subprocess
import sys
import time

# Event to signal the reception of new data
new_data_event = threading.Event()

def timer_thread(timeout=1.0):
    """Thread to handle the timer, which resets on receiving new data."""
    while True:
        if new_data_event.wait(timeout):  # Wait for the event or timeout
            print("New data received, resetting timer...")
            new_data_event.clear()  # Clear the event after it's set
        else:
            print("Timeout occurred, no new data within the timeout period. Terminating processes...")
            for name in list(processes.keys()):
                stop_process(name)
            break  # Exit the loop and end the thread if timeout expires without new data

def start_process(name, command):
    if name not in processes:
        print(f"Starting {name}...")
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
    """Thread to listen for new commands and process them."""
    try:
        while True:
            # Adjust select to monitor for reading and exceptions
            ready_to_read, _, in_error = select.select([sock], [], [sock], 0.1)
            if in_error:
                raise Exception("Socket error.")
            if ready_to_read:
                data = sock.recv(1024).decode().strip()
                if data:
                    print(f"Received command: {data}")
                    actions = ["burnburnburn", "linAlinAlinA", "solenoidsolenoidsolenoid", "pidpidpid", "unwindunwindunwind"]
                    if data in actions:
                        if processes.get(data) is None:
                            start_process(data, f'sleep 2; echo "Process for {data}"')
                        new_data_event.set()  # Reset the timer
                else:
                    print("Connection closed by the remote host.")
                    break
            else:
                print("No new command received, continuing existing processes...")
    except Exception as e:
        print(f"An error occurred in command listener: {e}")

# Create socket and connect in a non-blocking way
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setblocking(0)
try:
    sock.connect(('192.168.1.2', 1313))
except:
    pass
# Create and start threads
timer = threading.Thread(target=timer_thread, args=(1.0,))
listener = threading.Thread(target=command_listener)

timer.start()
listener.start()

# Main program continues here
try:
    # For demonstration, let's run this for a limited time then stop
    timer.join()
    listener.join()
except KeyboardInterrupt:
    print("Program interrupted by user.")
finally:
    # Close the socket and clean up processes
    sock.close()
    for name in list(processes.keys()):
        stop_process(name)
    print("Cleanup complete.")

print("Program terminated.")

