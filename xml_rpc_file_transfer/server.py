"""
@author - Parth Kalkar
To run - Download the file - open terminal in that folder -
         type "python3 server.py ip_address port"
"""
from xmlrpc.server import SimpleXMLRPCServer
from pathlib import Path
import os
import sys


# Send File Function
# Make sure to include file/s that you want to send in client folder
def send_file(file_name, data):
    file_path = Path("server/" + file_name)
    if file_path.exists():
        print(f"{file_name} not saved")
        return False, "File already exists"
    else:
        file_to_receive = open("server/" + file_name, 'wb')
        file_to_receive.write(data.data)
        print(f"{file_name} saved")
        return True, ""


# List of file Function
def list_files():
    list_of_files = os.listdir("server/")
    return list_of_files


# Delete File Function
def delete_file(file_name):
    file_path = Path("server/" + file_name)
    if file_path.exists():
        os.remove(file_path)
        print(f"{file_name} deleted")
        return True, ""
    else:
        print(f"{file_name} not deleted")
        return False, "File does not exists"


# Get File Function
def get_file(file_name):
    arr = file_name.split(" ")
    file_path = Path("server/" + file_name)
    if file_path.exists():
        file_to_send = open("server/" + file_name, 'rb')
        data = file_to_send.read()
        return True, data
    else:
        return False, "File does not exist!"


# Expression Calculator Function
def calculate(expression):
    """
    The implementation includes use of lambda expressions
    It has a dictionary of operators, followed by specific lambda expression
    It has following functions:
    1. is_int - to convert a number/string into integer
    2. is_float - to convert a number/string into float
    3. is_valid_number - to check if a number is valid either int or float
    4. type_converter - to convert as per type

    """

    operators_dict = {'+': lambda x, y: x + y,
                      '-': lambda x, y: x - y,
                      '*': lambda x, y: x * y,
                      '/': lambda x, y: x / y,
                      '>': lambda x, y: x > y,
                      '<': lambda x, y: x < y,
                      '>=': lambda x, y: x >= y,
                      '<=': lambda x, y: x <= y, }

    def is_int(integer_string):
        try:
            int(integer_string)
            return True
        except ValueError:
            return False

    def is_valid_number(number_string):
        if is_float(number_string) or is_int(number_string):
            return True
        return False

    def is_float(double_string):
        try:
            float(double_string)
            return True
        except ValueError:
            return False

    def type_converter(numeral_string):
        if is_int(numeral_string):
            return int(numeral_string)
        else:
            return float(numeral_string)

    split_string = expression.split(" ")
    if len(split_string) != 3:
        print(expression + " -- not done")
        return False, "The number of arguments is not equal to 3"

    operator = split_string[0]
    if operator not in operators_dict:
        print(expression + " -- not done")
        return False, f"{operator} is not a supported operator"
    if not is_valid_number(split_string[1]) or not is_valid_number(split_string[2]):
        print(expression + " -- not done")
        return False, f"Numbers should be provided"
    first_character = split_string[1]
    second_character = split_string[2]
    if operator == '/' and second_character == '0':
        print(expression + " -- not done")
        return False, "Division by zero"

    if (is_int(first_character) and
            is_int(second_character) and
            int(first_character) % int(second_character) == 0 and
            operator == '/'):
        return int(first_character) // int(second_character)

    print(expression + " -- done")
    return True, operators_dict[operator](type_converter(first_character), type_converter(second_character))


# exception handling for keyboard interrupt
try:
    with SimpleXMLRPCServer((sys.argv[1], int(sys.argv[2]))) as server:
        funcs = [get_file, calculate, send_file, list_files, delete_file]
        for i in funcs:
            server.register_function(i)
        server.serve_forever()
except KeyboardInterrupt:
    print("Server is stopping")
