"""
@author - Parth Kalkar
To run - Download the file - open terminal in that folder -
         type "python3 server2.py port"
"""
import socket
import sys
from datetime import datetime
import threading
import time

# dictionary of clients_info: clients_info[(adder, port)] = ReceivingClient
clients_info = {}

"""
MessageContent class contains: 
    a. type of message 
    b. sequence number

start message contains:  
    a. size of file (Kb, Mb, etc)
    b. extension (.png, .jpg, etc)

data message contains: 
    a. bytes of file
"""


class MessageContent:
    def __init__(self, received_data):
        self.time1 = datetime.timestamp(datetime.now())
        self.received = received_data
        message = str(received_data[0])[2:-1]
        self.address_port = received_data[1]
        data = message.split(" | ")
        self.message_type = data[0]
        self.seq_no = data[1]

        if self.message_type == "s":
            self.ext = data[2]
            self.file_size = int(data[3])
            self.file_name = "new_" + str(self.address_port[0]) + "_" + str(self.address_port[1]) + "." + self.ext

        if self.message_type == "d":
            bytes_length = len(data[2])
            full_length = len(message)
            self.bytes = received_data[0][full_length - bytes_length:]


"""
ReceivingClient class containing: 
    a. current sequential number 
    b. timestamp,
    c. content
"""


class ReceivingClient:
    received_bytes = 0
    seq_no = 0
    content = {}

    def __init__(self, address_port, file_name, file_size, file_extension):
        self.address_port = address_port
        self.file_size = file_size
        self.file_ext = file_extension
        self.file_name = file_name
        self.timestamp = datetime.timestamp(datetime.now())

    def file_received(self):
        if self.received_bytes == self.file_size:
            return True
        return False

    def save_file(self):
        file = open(self.file_name, 'wb')
        for i in range(0, self.seq_no):
            file.write(self.content[i].bytes)
        file.close()

    def increase_received_bytes(self, length):
        self.received_bytes = self.received_bytes + length

    def add_content(self, content):
        self.content[self.seq_no] = content
        self.seq_no = self.seq_no + 1
        self.timestamp = datetime.timestamp(datetime.now())


# localIP and localPort
host = socket.gethostname()  # Get local machine name
local_ip = socket.gethostbyname(host)  # localIP = "127.0.0.1"
local_port = int(sys.argv[1])  # localPort = 20001
print("UDP server is on... ")
print("Got a connection from: ", host, "with IP: ", local_ip)

# socket address
server_address = (local_ip, local_port)

# socket creation
server_udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# socket binding 
server_udp_socket.bind(server_address)

max_size = 1024


# client's activity checker function
# info about delivery of file
# kicking out mechanism
def client_activity_checker(ip_address, delivery_port):
    while True:
        timestamp = datetime.timestamp(datetime.now())

        if clients_info[(ip_address, delivery_port)].file_received():
            print(f"The file by {(ip_address, delivery_port)} has been received.")

            # save file 
            # keep data for a sec
            clients_info[next_message.address_port].save_file()
            time.sleep(1)
            del clients_info[(ip_address, delivery_port)]
            break

        if timestamp - clients_info[(ip_address, delivery_port)].timestamp >= 3 and \
                not clients_info[(ip_address, delivery_port)].file_received():
            print(f"The client {(ip_address, delivery_port)} has been kicked out for being inactive for 3 seconds!")
            print("To connect restart...")
            del clients_info[(ip_address, delivery_port)]
            break


while True:
    try:

        receive_from = server_udp_socket.recvfrom(max_size)

        # receiving next message
        next_message = MessageContent(receive_from)

        """

        for start message: 
            a. create a new client in dictionary
            b. check their activity
            c. send ack message
        
        """
        if next_message.message_type == "s":
            print(f"Receiving from {next_message.address_port}")
            new_client = ReceivingClient(next_message.address_port, next_message.file_name, next_message.file_size,
                                         next_message.ext)

            clients_info[next_message.address_port] = new_client
            thread1 = threading.Thread(target=client_activity_checker, args=next_message.address_port)
            thread1.start()

            ack_message = "a | " + str(clients_info[next_message.address_port].seq_no) + " | " + str(max_size)
            server_udp_socket.sendto(ack_message.encode(), next_message.address_port)

        """
        
        for data message: 
            a. add content
            b. send ack message
            c. increment received bytes
                    
        """
        if next_message.message_type == "d":

            clients_info[next_message.address_port].add_content(next_message)

            ack_message = "a | " + str(clients_info[next_message.address_port].seq_no)

            server_udp_socket.sendto(ack_message.encode(), next_message.address_port)

            clients_info[next_message.address_port].increase_received_bytes(len(next_message.bytes))

    except KeyboardInterrupt:
        sys.exit()
