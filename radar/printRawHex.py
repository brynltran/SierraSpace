import serial
import time
import struct
# Serial port configuration
port_name = '/dev/ttyACM1'  # Adjust as per your setup
baud_rate = 921600  # Set this to the baud rate of your radar sensor

def read_serial_data(port, baud, timeout=1):
    with serial.Serial(port, baud, timeout=timeout) as ser:
        print(f"Opening {port} at {baud} baud rate.")
        while True:
            if ser.inWaiting() > 0:
                data = ser.readline()
                print(data)

if __name__ == '__main__':
    try:
        read_serial_data(port_name, baud_rate)
    except KeyboardInterrupt:
        print("Stopped by the user")

