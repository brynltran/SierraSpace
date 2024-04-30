import socket
import time

ip = '192.168.1.2'
host = 1013

def connect_to_server():
    while True:
        try:
            clientSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSoc.connect((ip, host))
            print("Successfully connected to server")
            return clientSoc
        except socket.error as e:
            print("No connection found, retrying in 1 second")
            time.sleep(1)

def handle_communication():
    client_socket = connect_to_server()
    try:
        while True:
           msg = client_socket.recv(1024).decode('utf-8')
           print(msg)
           time.sleep(0.5)

    except socket.error:
        print('Disconnected from server. Now listening for new connections...')
        client_socket.close()
        handle_communication() #Recursively calls itself upong disconnect
        time.sleep(0.5)


def main():
   handle_communication() 


if __name__=='__main__':
    main()
