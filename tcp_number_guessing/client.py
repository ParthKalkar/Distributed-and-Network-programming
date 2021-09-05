"""
@author - Parth Kalkar
To run - Download the file - open terminal in that folder -
         type "python3 client.py port"

** Make sure that the server.py is running before running this file **

"""

import socket
import sys

# exception handling for port
try:
    global server_port
    server_port = int(sys.argv[1])
except IndexError:
    print("Usage example: python./server.py <port>")
    sys.exit()

# server_ip, buffer size and adapting connection
server_ip = "127.0.0.1"
buffer_size = 1024
client_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# exception handling to connect in 5s
try:
    client_tcp_socket.settimeout(5)
    client_tcp_socket.connect((server_ip, server_port))
    server_port_message = client_tcp_socket.recv(buffer_size)
except socket.timeout:
    print("Cannot connect to the server")

# if server is full, client is informed
if server_port_message == "The server is full!".encode():
    print("The server is full!")
    sys.exit()

# closing previous socket
client_tcp_socket.close()

# starting new socket
client_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_tcp_socket.connect((server_ip, int(str(server_port_message, "utf-8"))))
print(str(client_tcp_socket.recv(buffer_size), "utf-8"), end="")

# exception handling for sending info to server
try:
    # send range
    _input = input()
    client_tcp_socket.sendall(str(_input).encode())

    while attempt_msg := client_tcp_socket.recv(buffer_size):
        print(str(attempt_msg, "utf-8"))
        print("Your guess: ", end="")

        # send number
        _input = input()
        client_tcp_socket.sendall(str(_input).encode())

        reply_message = client_tcp_socket.recv(buffer_size)
        print(str(reply_message, "utf-8"))

        client_tcp_socket.sendall("OK".encode())
except KeyboardInterrupt:
    client_tcp_socket.close()
    sys.exit()
