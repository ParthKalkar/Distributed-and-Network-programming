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
import node
import registry

# Exception Handling to avoid incorrect inputs
try:
    m, first_port, last_port = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])

    if m != 5:
        print("Wrong value entered for m - It should be 5, Retry!")
        sys.exit()

except IndexError:
    print("Usage example: python3 main.py <m> <first_port> <last port>")
    sys.exit()

registry_thread = registry.Registry(m)
registry_thread.start()
nodes = {}

for i in range(last_port - first_port + 1):
    node_thread = node.Node(first_port + i, registry_thread)
    nodes[first_port + i] = node_thread
    node_thread.start()

print(f"Registry and {last_port - first_port + 1} nodes are created.")

# Exception handling to manage commands
try:
    while True:
        command = input().split(" ")


        def handle_chord_info():
            print(registry_thread.get_chord_info())


        def handle_finger_table():
            print(nodes[int(command[1])].get_finger_table())


        def handle_no_command():
            print("No command entered, Retry! ...")


        {'get_chord_info': handle_chord_info,
         'get_finger_table': handle_finger_table,
         '': handle_no_command}[command[0]]()

except KeyboardInterrupt:
    print("\nKeyboard Interrupt ... ")
    sys.exit()

except KeyError:
    print("\nKey Error ...")
    sys.exit()
