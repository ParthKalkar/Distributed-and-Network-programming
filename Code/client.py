import socket
import sys

host = socket.gethostname()  # Get local machine name
local_ip = socket.gethostbyname(host)
local_port = int(sys.argv[2])

serverAddressPort = (local_ip, local_port)
bufferSize = 1024



c = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

while True:
    equ = input("Input regular expression for calculation: ")
  
    sent_bytes = str.encode(str(equ))
    c.sendto(sent_bytes, serverAddressPort)

    server_message = c.recvfrom(bufferSize)
    equ = format(server_message[0])


    print(f"Result: {equ[2: -1]}\n")
   
    
