"""
@author - Parth Kalkar
To run - Download the file - open terminal in that folder -
         type "python3 client.py"

** Make sure that the server.py is running before running this file **

** Also, make sure you have config file in the same folder **

"""

from xmlrpc.client import ServerProxy

print("The client starts.")
server = None

# exception handling for input commands and the necessary actions
try:
    while True:
        command = input("> ").split()
        if command[0] == 'connect':
            try:
                server = ServerProxy(f'http://{command[1]}:{command[2]}')
            except IndexError:
                print("Index Error, Enter a correct value")
        if command[0] == 'getleader':
            print(server.get_leader())
        if command[0] == 'suspend':
            print(server.suspend(int(command[1])))
        elif command[0] == 'quit':
            break
except KeyboardInterrupt:
    print("\nThe client ends.")
