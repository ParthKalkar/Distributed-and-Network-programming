"""
@author - Parth Kalkar
To run - Download the file - open terminal in that folder -
         type "python3 client2.py ip_address port"

** Make sure that the server2.py is running before running this file **

** Also, make sure you have innopolis.jpg or any file that you wanna send in the same folder **

"""

import os
import pathlib
import socket
import sys

# socket creation
client_udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


# Binary string formatting function
def format_string(string):
    return str(string)[2:-1]


max_size = 1024

# localIP and localPort
host = socket.gethostname()  # Get local machine name
local_ip = socket.gethostbyname(host)  # localIP = "127.0.0.1"
local_port = int(sys.argv[2])  # localPort = 20001

print(f"Enter the file you want to share\n> ", end="")

file_name = input()

try:
    file = open(file_name, 'rb')
except FileNotFoundError:
    print("File not found, add the desired file to send and try again :( ")
    sys.exit()

file.seek(0, os.SEEK_END)
file_size = file.tell()
file_ext = pathlib.Path(file.name).suffix

seq_no = 0

# socket address
server_address = (local_ip, local_port)


# Receive ack function
def receive_ack(message, start_message=False):
    for trial_count in range(6):
        try:
            if trial_count != 0:
                print(f"Trying to establish connection with the server with trial number: "
                      f"{trial_count}", end="\r")

            client_udp_socket.sendto(message, server_address)
            client_udp_socket.settimeout(0.5)

            sys.stdout.write("\033[K")

            # for successful ack, take it's seq_no
            if ack_message := client_udp_socket.recvfrom(128):
                ack_array = format_string(ack_message[0]).split(" | ")
                global seq_no
                seq_no = int(ack_array[1])

                # for start message ack, save max size
                if start_message:
                    global max_size
                    max_size = int(ack_array[2])

                return True

            client_udp_socket.settimeout(None)

        except socket.timeout:
            if trial_count == 5:
                sys.stdout.write("\033[K")
    return False


# initial message to send
initial_message = ("s | " + str(seq_no) + " | " + str(file_ext)[1:] + " | " + str(file_size)).encode()

# send start message
# receive ack for it 
# open file
if receive_ack(initial_message, True):
    file = open(file_name, 'rb')

# read file 
# send its bytes 
# receiving ack
while next_bytes := file.read(max_size - len("d | " + str(seq_no) + " | ")):
    data_message = ("d | " + str(seq_no) + " | ").encode() + next_bytes
    receive_ack(data_message)

# close file
file.close()

# exit program
sys.exit()
