"""
@author - Parth Kalkar
To run - Download the file - open terminal in that folder -
         type "python3 client.py ip_address port"

** Make sure that the server.py is running before running this file **

"""

from xmlrpc.client import ServerProxy
from pathlib import Path
import sys

with ServerProxy(f"http://{sys.argv[1]}:{int(sys.argv[2])}/") as proxy:

    # Quit Function
    def quit_():
        sys.exit()

    # Send File Function
    def send(file_name):
        try:
            file_to_send = open("client/" + file_name, 'rb')
            data = file_to_send.read()
            output, message = proxy.send_file(file_name, data)
            if output:
                print("Completed!")
            else:
                print("Not completed!\n", message)
        except FileNotFoundError:
            print("File not found.. ")

    # Receive File List Function
    def list_():
        print(proxy.list_files())

    # Delete File Function
    def delete(_str):
        result, message = proxy.delete_file(_str)
        if result:
            print("Completed!")
        else:
            print("Not completed! \n", message)

    # Get File Function
    def get(file_name):
        file_name_split = file_name.split(" ")
        if (len(file_name_split) == 1 and Path("client/" + file_name_split[0]).exists() or
                len(file_name_split) == 2 and Path("client/" + file_name_split[1]).exists()):
            print("Not completed!", "\n File already exists")
            return

        output = proxy.get_file(file_name_split[0])

        if output[0]:
            if len(file_name_split) == 1:
                file_to_get = open("client/" + file_name_split[0], 'wb')
                file_to_get.write(output[1].data)
            if len(file_name_split) == 2:
                file_to_get = open("client/" + file_name_split[1], 'wb')
                file_to_get.write(output[1].data)
            print("Completed!")
        else:
            print("Not completed!\n", output[1])

    # Calc Function
    def calc(expression):
        result = proxy.calculate(expression)
        if result[0]:
            print(result[1], "\nCompleted!")
        else:
            print("Not completed!\n", result[1])

    # main loop
    # exception handling for keyboard interrupt
    try:
        while True:
            print("Enter command: ", end="")
            command = input()
            command_split = command.split(" ")
            function_list_1 = {
                "quit": quit_,
                "list": list_
            }
            function_list_2 = {
                "send": send,
                "get": get,
                "delete": delete,
                "calc": calc
            }
            if command_split[0] in function_list_1:
                function_list_1[command_split[0]]()

            elif command_split[0] in function_list_2:
                function_list_2[command_split[0]](command.replace(command_split[0] + " ", ''))

            else:
                print("Command not found!")

            print()

    except KeyboardInterrupt:
        print("\n Client is stopping")
        sys.exit()
