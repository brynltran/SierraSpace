import threading
import socket
import select
import subprocess
import sys
import time
import errno
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

def start_solenoid():
    GPIO.output(14, GPIO.HIGH)
    time.sleep(5)
    GPIO.output(14, GPIO.LOW)


# Global job list with a dictionary containing job names and their corresponding timeouts
jobs = {}
processes = {}

# Event to signal the reception of new data
new_data_event = threading.Event()

def timer_thread(interval=1.0):
    """Thread to handle the tracking of jobs and their timeouts."""
    while True:
        time.sleep(interval)
        expired_jobs = [job for job, timeout in jobs.items() if timeout <= 0]
        for job in expired_jobs:
            print(f"Job {job} has timed out. Terminating...")
            stop_process(job)

def add_job(name, command, timeout):
    """Start a new job process and add it to the job list with a timeout."""
    if name not in processes:
        print(f"Starting job {name}...")
        processes[name] = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        jobs[name] = timeout  # Set the initial timeout for the job
    else:
        print(f"Job {name} is already running. Resetting timeout...")
        jobs[name] = timeout  # Reset the timeout for the job

def stop_process(name):
    """Terminate a job process."""
    if name in processes:
        print(f"Stopping job {name}...")
        processes[name].terminate()
        processes[name].wait()
        del processes[name]
    if name in jobs:
        del jobs[name]

def command_listener(sock, timeout=10):
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
                    actions = ["burn", "linA", "solenoid", "pid", "unwind"]
                    if data in actions:
                        add_job(data, f'sleep 2; echo "Process for {data}"', timeout)
                        new_data_event.set()  # Reset the timer
                else:
                    print("Connection closed by the remote host.")
                    break
            else:
                # Reduce the timeout for all jobs since no new command was received
                for job in jobs:
                    jobs[job] -= 0.1
                print("No new command received, continuing existing processes...")
    except Exception as e:
        print(f"An error occurred in command listener: {e}")

# Main program starts here
if __name__ == "__main__":
    # Create socket and connect in a non-blocking way
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(0)
    try:
        sock.connect(('192.168.1.2', 1313))
    except socket.error as e:
        if e.errno != errno.EINPROGRESS:
            print(f"Error connecting to socket: {e}")
            sock.close()
            sys.exit(1)

    # Create and start threads
    timer = threading.Thread(target=timer_thread, args=(1.0,))
    listener = threading.Thread(target=command_listener, args=(sock,))

    timer.start()
    listener.start()

    try:
        # Main thread will check every second for keyboard interrupt to allow graceful shutdown
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        # Close the socket and clean up processes
        sock.close()
        GPIO.cleanup()
        for name in list(processes.keys()):
            stop_process(name)
        print("Cleanup complete.")

    print("Program terminated.")

