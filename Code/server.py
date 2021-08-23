import socket
import sys

bufferSize = 1024
host = socket.gethostname()  # Get local machine name # localIP = "127.0.0.1"
local_ip = socket.gethostbyname(host)  # localPort = 20001
local_port = int(sys.argv[1])

s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

s.bind((local_ip, local_port))
print("UDP server is on")
print("Got a connection from: ", host, "with IP: ", local_ip)

data = []
result = 0


def cal(opr, arg1, arg2):
    return eval(arg1 + opr + arg2)


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def all_int(string1, string2):
    if string1.isnumeric() and string2.isnumeric():
        return True
    return False


while True:
    error = False
    bytesAddressPair = s.recvfrom(bufferSize)

    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    clientMsg = format(message)
    clientIP = format(address)

    operators = ['+', '-', '/', '*', '<', '>', '<=', '>=', '==']
    arr = [i for i in (clientMsg[2 : -1]).split()]

    try:
        if arr[0].lower() == 'quit' or Keyboard:
            print("Keyboard interrupt and STOP!")
            break
        elif len(arr) != 3 or arr[0] not in operators or not is_number(arr[1]) or not is_number(arr[2]):
            result = "Invalid Input"
            error = True
        else:
            result = cal(arr[0], arr[1], arr[2])
            data.append(result)
            print(result)

        if not error:
            if not all_int(arr[1], arr[2]):
                result = float(result)
            elif arr[0] == "/" and float(result) != int(result):
                result = float(result)
            elif arr[0] == "/" and float(result) == int(result):
                result = int(result)
            else:
                result = int(result) 
               
    except ZeroDivisionError:
        print("ZeroDivision")
        result = "Zero Division"
    except KeyboardInterrupt: 
        sys.exit()

    sent_bytes = str.encode(str(result))
    s.sendto(sent_bytes, address)
