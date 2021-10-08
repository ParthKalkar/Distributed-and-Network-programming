"""
@author - Parth Kalkar
To run - Download the file - open terminal in that folder -
         type "python3 client1.py ip_address port"

** Make sure that the server1.py is running before running this file **

** Also, make sure you have innopolis.jpg or any file that you wanna send in the same folder **

"""

import binascii
import os
import socket
import json
import sys
import time

# localIP and localPort
host = socket.gethostname()  # Get local machine name
local_ip = socket.gethostbyname(host)  # localIP = "127.0.0.1"
local_port = int(sys.argv[2])  # localPort = 20001


# Checksum Function
def checksum(file_contents):
    file_contents = (binascii.crc32(file_contents) & 0xFFFFFFFF)
    return "%08X" % file_contents


# Exit Function
def to_exit():
    for i in range(10):
        print(f"The system is Shutting down in {10 - i}...", end="\r")
        time.sleep(2)
    sys.exit()


# Json Converter Function
def json_converter(file_information):
    return file_information.toJSON()


# open picture
print(f"Enter the filename (from the folder)\n> ", end="")
pic = open(input(), 'rb')
pic_checksum = checksum(pic.read())
pic.seek(0, os.SEEK_END)

# fill dictionary fields
file_info = {'checksum': pic_checksum, 'name': pic.name, 'size': pic.tell()}
pic.close()

# server address - serverIP & serverPort
server_address = (local_ip, local_port)

# socket creation
udp_transfer_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


# Send Function
def send_to_server():

    # convert to json and send
    data = json.dumps(file_info, default=json_converter, indent=2)
    udp_transfer_socket.sendto(data.encode(), server_address)

    # get the bufferSize within a second
    try:
        udp_transfer_socket.settimeout(1.0)
        bufferSize = udp_transfer_socket.recvfrom(32)
        udp_transfer_socket.settimeout(None)

    # if time surpasses then shut down
    except socket.timeout:
        print("Server unavailable. Try Again Later")
        udp_transfer_socket.close()
        to_exit()

    # if message received is not bufferSize then shut down
    if not str(json.loads(bufferSize[0])).isnumeric():
        print("Server unavailable. Try Again Later")
        udp_transfer_socket.close()
        to_exit()

    bufferSize_int = int(json.loads(bufferSize[0]))

    # open file to send
    image_to_send = open(file_info['name'], "rb")

    # traverse until data can be sent
    while next_byte := image_to_send.read(bufferSize_int):
        udp_transfer_socket.sendto(next_byte, server_address)

    # inform the server when done
    udp_transfer_socket.sendto("Done".encode(), server_address)

    # try to get the "OK" message within one second
    try:
        udp_transfer_socket.settimeout(1.0)
        message_to_control = udp_transfer_socket.recvfrom(32)
        udp_transfer_socket.settimeout(None)

        if message_to_control[0] == "OK".encode():
            print("The picture has been uploaded successfully. To resend restart!")
            to_exit()

        # if we didnt receive OK then repeat
        else:
            print("Something went wrong, trying again...")
            send_to_server()

    # if time exceeds then shut down
    except socket.timeout:
        print("Server error. Try again later... ")
        udp_transfer_socket.close()
        to_exit()


# start to send
send_to_server()
