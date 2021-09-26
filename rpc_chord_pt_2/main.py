"""
Author - Parth Kalkar

This is the main.py file. It should accept three arguments: m, first_port, and last_port.
- m represents the length of identifiers in chord (in bits) and has default value of 5.
- first_port and last_port represent the range of port numbers that the nodes are going to use.

To run -

1. Unzip the folder
2. Open the terminal in that folder
3. Write command - main.py m first_port last_port.

"""
import sys
import time
import zlib
from xmlrpc.client import ServerProxy

from registry import Registry
from node import Node

registry_ip = '127.0.0.1'

m, first_port, last_port = 5, 0, 0

try:
    m, first_port, last_port = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])

    if m != 5:
        print("Wrong value entered for m - It should be 5, Retry!")
        sys.exit()

except IndexError:
    print("Usage example: python3 main.py <m> <first_port> <last port>")
    sys.exit()

registry_port = last_port + 1

registry_boolean, no_of_attempts = None, 5

while registry_boolean is None:
    registry_boolean = Registry(m, registry_ip, registry_port)
    no_of_attempts -= 1
    time.sleep(0.2)
    if not registry_boolean.is_alive():
        registry_boolean = None
        registry_port += 1
    if not no_of_attempts:
        print("Failed to find a port for the Registry XMLRPC Server after 5 attempts.\nExiting ...")
        exit(1)

registry_server = ServerProxy(f'http://{registry_ip}:{registry_port}')

nodes = [Node(m, i, registry_ip, registry_port) for i in range(first_port, last_port + 1)]

time.sleep(1)

for node in nodes:
    if not node.is_alive():
        if node.id == -1:
            print(f"Couldn't start node on port {node.port} ({node.registration_message})\nExiting ...")
        else:
            print(f"Couldn't start node on port {node.port}.\nExiting ...")
        for i_ in nodes:
            try:
                i_.kill()
            except Exception as e:
                pass
        registry_boolean.kill()
        exit(1)

time.sleep(0.5)

node_servers = {}

for node in range(first_port, last_port + 1):
    node_server = ServerProxy(f'http://127.0.0.1:{node}')
    node_servers[str(node)] = node_server

print(f"Registry and {last_port - first_port + 1} nodes are created. ")
while True:
    try:
        command= input("> ").split()
        if command[0] == 'get_chord_info':
            print(eval(f"registry_server.{command[0]}({','.join(command[1:])})"))
        elif command[0] == 'get_finger_table':
            print(eval(f"node_servers['{command[1]}'].{command[0]}({','.join(command[2:])})"))
        elif command[0] == 'quit':
            if command[1] not in node_servers:
                print(f"Node with port {command[1]} isn’t available")
            print(node_servers[command[1]].quit())

        elif command[0] == 'save':
            hash_value = zlib.adler32(command[2].encode())
            target_id = hash_value % 2 ** m
            print(f"{command[2]} has identifier {target_id}")
            print(node_servers[command[1]].savefile(command[2]))
        elif command[0] == 'get':
            hash_value = zlib.adler32(command[2].encode())
            target_id = hash_value % 2 ** m
            print(f"{command[2]} has identifier {target_id}")
            print(node_servers[command[1]].getfile(command[2]))
        else:
            print("Invalid command.")
    except KeyboardInterrupt:
        registry_boolean.join()
        for node in nodes:
            node.join()
        print("Keyboard Interrupt...")
        exit(0)
    except Exception as e:
        print(f"Invalid command ({e})")
