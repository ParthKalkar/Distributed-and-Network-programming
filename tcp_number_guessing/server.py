"""
@author - Parth Kalkar
To run - Download the file - open terminal in that folder -
         type "python3 server.py port"
"""
import socket
import sys
import threading
import random

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
server_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# exception handling while binding
try:
    server_tcp_socket.bind((server_ip, server_port))
except socket.error:
    print("Error while binding to the specified port")
    sys.exit()

# server is set
print(f"Starting the server on {server_ip}:{server_port}")
server_tcp_socket.listen()

# number of players
player_count = 0


# Finish Game Function
def finish_game(game_connection, message):
    if message:
        game_connection.sendall(message.encode())
    game_connection.close()
    global player_count
    player_count = player_count - 1


# New Connection Function
def setup_new_conn(new_client):
    try:
        game_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        game_tcp_socket.settimeout(5)
        game_tcp_socket.bind((server_ip, 0))
        game_tcp_socket.listen()

        new_client.sendall(f"{game_tcp_socket.getsockname()[1]}".encode())
        new_client.close
        game_conn = game_tcp_socket.accept()[0]
    except socket.timeout:
        return None

    return game_conn


"""
Game Logic Function

- new connection set up
- Send welcome message
- receive range
- Receive attempts to guess

"""


def game_logic(new_player):
    game_connection = setup_new_conn(new_player)
    if not game_connection:
        return

    global player_count
    player_count = player_count + 1
    game_connection.sendall("Welcome to the number guessing game!\nEnter the range: ".encode())

    range_message = str(game_connection.recv(buffer_size), "utf-8")
    if range_message == "":
        finish_game(game_connection, "")
        return

    _range = int(range_message.split(" ")[0]), int(range_message.split(" ")[1])

    number_to_guess = int(random.uniform(_range[0], _range[1]))

    for attempt in range(5, 0, -1):
        game_connection.sendall(f"You have {attempt} attempts".encode())

        next_number_str = str(game_connection.recv(buffer_size), "utf-8")

        next_number = int(next_number_str)

        if next_number == number_to_guess:
            finish_game(game_connection, "You won!")
            return
        elif attempt == 1:
            finish_game(game_connection, "You lose")
            return
        elif number_to_guess > next_number:
            game_connection.sendall("Greater!".encode())
            game_connection.recv(buffer_size)
        else:
            game_connection.sendall("Less".encode())
            game_connection.recv(buffer_size)


# exception handling for multiple users
try:
    while True:
        if player_count <= 2:
            print("Waiting for a connection")

            client_connection, client_ip = server_tcp_socket.accept()
            if player_count == 2:
                print("The server is full")

        if player_count < 2:
            print("Client connected")
            game_thread = threading.Thread(target=game_logic, args=(client_connection,))
            game_thread.daemon = True
            game_thread.start()
        else:
            client_connection.sendall("The server is full!".encode())
            client_connection.close()
except KeyboardInterrupt:
    sys.exit()
