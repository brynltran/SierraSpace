import socket
import time
import time
import RPi.GPIO as GPIO
import subprocess


def solenoid():
    GPIO.setup(14, GPIO.OUT)
    GPIO.output(14, GPIO.HIGH)
    time.sleep(5)
    GPIO.output(14, GPIO.LOW)

def process_start(x):
    try:
        print(x)
    finally:
        GPIO.cleanup()

def start_client():
    host = '192.168.1.2'  # The server's hostname or IP address
    port = 1313        # The port used by the server

    while True:
        try:
            # Create a socket object
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Connect to the server
            client_socket.connect((host, port))
            print("Connected to server:", host, port)
            
            while True:
                # Send data
                print('hi')
                temp = client_socket.recv(1024)
                data = temp.decode()
                print('Received from server:', data)
                process_start(data)
                # Sleep for a while before sending next data
                time.sleep(0.1)
        
        except socket.error as e:
            print("Error:", e)
            print("Attempting to reconnect...")
            time.sleep(3)  # Wait a bit before trying to reconnect
        
        finally:
            client_socket.close()
            GPIO.cleanup()

if __name__ == '__main__':

    GPIO.setmode(GPIO.BCM)
    start_client()

