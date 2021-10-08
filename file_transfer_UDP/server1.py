"""
@author - Parth Kalkar
To run - Download the file - open terminal in that folder -
         type "python3 server1.py port"
"""

import binascii
import socket
import json
import sys

# localIP and localPort
host = socket.gethostname()  # Get local machine name
local_ip = socket.gethostbyname(host)  # localIP = "127.0.0.1"
local_port = int(sys.argv[1])  # localPort = 20001
print("UDP server is on... ")
print("Got a connection from: ", host, "with IP: ", local_ip)

# socket creation
udp_transfer_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# socket binding
udp_transfer_socket.bind((local_ip, local_port))

# bufferSize
bufferSize = 1024


# Checksum Function
def checksum(file_contents):
    file_contents = (binascii.crc32(file_contents) & 0xFFFFFFFF)
    return "%08X" % file_contents


# Receive Function
def receive_from_client():
    # using a try - catch block to avoid any kind of exception/error
    try:
        string_data = udp_transfer_socket.recvfrom(1024)
        file_info = json.loads(string_data[0])
        print(f"Receiving {file_info}\nby {string_data[1]}")
        udp_transfer_socket.sendto(str(bufferSize).encode(), string_data[1])

    except KeyboardInterrupt:
        sys.exit()

    # if the previous block is executed properly then
    # we open a new file with a corresponding name
    image_to_receive = open("new_" + file_info["name"], 'wb')

    # trying to get all the bytes in a loop
    try:
        process_is_on = True
        while process_is_on:
            next_bytes = udp_transfer_socket.recvfrom(bufferSize)
            if not next_bytes[0] == "Done".encode():
                image_to_receive.write(next_bytes[0])
            else:
                break

    # if an error occurs then restart
    except:
        print("Error occurred while receiving client's image. Please try again... ")
        sys.exit()

    # if everything is ok then close the file
    image_to_receive.close()

    # reopen it in reading mode to get its checksum
    image_to_receive = open("new_" + file_info["name"], 'rb')
    image_checksum = checksum(image_to_receive.read())

    # if the checksums match then send "OK" to the client
    if image_checksum == file_info["checksum"]:
        udp_transfer_socket.sendto("OK".encode(), string_data[1])
        print(f"The file \'{image_to_receive.name}\' has been received successfully\n")
    else:
        print(f"The checksums do not much. The previously downloaded file has been removed!\n")


# start to receive
while True:
    receive_from_client()
