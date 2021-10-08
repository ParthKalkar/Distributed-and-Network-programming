"""
@author - Parth Kalkar
To run - Download the file - open terminal in that folder -
         type "python3 server.py id"
"""

import sys
import time
from threading import Thread, Lock
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
from datetime import datetime
import random
import socket

# default socket timeout
socket.setdefaulttimeout(2)

# initialising term, time-span and timer
term = 0
time_span = [150, 350]
timer = random.randint(*time_span)

# initialising suspended, period and start
suspended, suspended_period, suspended_start = False, 1, datetime.utcnow()

# introducing server list and names
server_list = []
server_names = {}

# initialising voted, state and leader
voted, state, leader = False, 'follower', None

# initialising timer, timeout and last timer
reset_timer, timeout, reset_last_timer = False, False, datetime.utcnow()

lock_timer = Lock()
lock_state_leader = Lock()
mutex = Lock()

# getting ID, using try catch to avoid invalid inputs
id_ = None
try:
    id_ = int(sys.argv[1])
except IndexError:
    print("Invalid arguments.")
    sys.exit()

# getting IP address and port of the server from the config file
ip_address, port = None, None

with open('config.conf') as configfile:
    config_lines = configfile.readlines()
    for line_element in config_lines:
        line_element = line_element.strip('\n').split()
        server_names[str(line_element[0])] = f"{line_element[1]}:{line_element[2]}"

        if line_element[0] == str(id_):
            ip_address, port = line_element[1], int(line_element[2])
        else:
            server_list.append(f"http://{line_element[1]}:{line_element[2]}")

# conditional checking for missing ip or port
if ip_address is None or port is None:
    print("ID not found in the config file. Shutting down ...")
    sys.exit()

print(f"Server is started at {ip_address}:{port}", "\nI am a follower. Term: 0")


# Custom RPC Class
class CustomXMLRPCServer(SimpleXMLRPCServer):
    def serve_forever(self):
        while not suspended:
            self.handle_request()
            time.sleep(0.003)


# Request Vote Function
def request_vote(candidate_term, candidate_id):
    global term, voted, state, leader
    mutex.acquire()
    lock_timer.acquire()
    leader = ""
    if suspended and (datetime.utcnow() - suspended_start).total_seconds() < suspended_period:
        return "suspended", False

    if candidate_term > term:
        term = candidate_term
        state = 'follower'
        voted = False

    if not voted and candidate_term == term:
        voted = True
        state = 'follower'
        print(f"Voted for node {candidate_id}")
        leader = candidate_id
        mutex.release()
        lock_timer.release()
        return term, True
    mutex.release()
    lock_timer.release()
    return term, False


# Append Entry Function
def append_entry(leader_term, leader_id):
    global leader, term, reset_timer, timeout, lock_timer, voted, state
    lock_timer.acquire()

    if leader_term >= term:
        state = 'follower'
        term = leader_term
        lock_timer.acquire()
        reset_timer = True
        timeout = False
        lock_timer.release()
        leader = leader_id

        if voted:
            voted = False
            print(f"I am a follower. Term: {term}")

        print(f"Heartbeat from {leader_id}")
        return term, True
    lock_timer.release()
    return term, False


# Get leader Function
def get_leader():
    if suspended and (datetime.utcnow() - suspended_start).total_seconds() < suspended_period:
        return False
    print(f"Command from client: getleader")
    result = ""
    if leader != "":
        result = f"{leader} {server_names[str(leader)]}"
    print(result)
    return result


# Suspend Function
def suspend(period):
    global suspended, suspended_period, suspended_start
    if suspended and (datetime.utcnow() - suspended_start).total_seconds() < suspended_period:
        return False
    print(f"Command from client: suspend {period}")
    suspended = True
    suspended_period = int(period)
    suspended_start = datetime.utcnow()
    print(f"Sleeping for {period} seconds")
    return True


# RPC Server Function
def rpc_server():
    server = CustomXMLRPCServer((ip_address, port), logRequests=False)
    funcs = [request_vote, append_entry, get_leader, suspend]
    for f in funcs:
        server.register_function(f)
    while True:
        server.serve_forever()


# RPC Client Function
def rpc_client():
    global state, term, id_, suspended_period, suspended_start, suspended, timeout, \
        reset_timer, leader, lock_timer, voted
    rpc_clients = [ServerProxy(some_server) for some_server in server_list]

    while True:
        if suspended and (datetime.utcnow() - suspended_start).total_seconds() < suspended_period:
            continue
        if state == 'leader':
            for rpc_c in rpc_clients:
                try:
                    peer_term, approved = rpc_c.append_entry(term, id_)
                except:
                    continue
                if peer_term > term:
                    term = peer_term
                    voted = False
                    state = 'follower'
                    print(f"I am a follower. Term: {term}")
                    break
            time.sleep(0.05)
            reset_timer = True
            continue
        lock_timer.acquire()

        if timeout and not voted:
            timeout = False
            if state == 'follower':
                print('The leader is dead')

                state = 'candidate'
                term += 1
                print(f"I am a candidate. Term: {term}")

                reset_timer = True
                timeout = False
                lock_timer.release()

                votes = 1
                voted = True
                refused = 0
                print(f"Voted for node {id_}")

                for rpc_c in rpc_clients:
                    if timeout:
                        break
                    try:
                        peer_term, approved = rpc_c.request_vote(term, id_)
                    except:
                        continue

                    if peer_term == 'suspended':
                        continue

                    if peer_term > term:
                        term = peer_term
                        voted = False
                        state = 'follower'
                        break

                    if approved:
                        votes += 1
                    else:
                        refused += 1

                print(f"Votes received")

                time.sleep(0.05)
                lock_timer.acquire()

                if state == 'follower' or timeout or refused > votes:
                    timeout = False
                    state = 'follower'
                    print(f"I am a follower. Term: {term}")
                    reset_timer = True
                    continue

                state = 'leader'
                leader = id_
                reset_timer = True
                print(f"I am a leader. Term: {term}")

        lock_timer.release()


# Timer Thread Function
def timer_thread():
    global reset_last_timer, reset_timer, timeout, suspended, state

    while True:
        lock_timer.acquire()

        if suspended and (datetime.utcnow() - suspended_start).total_seconds() < suspended_period:
            continue

        if suspended:
            state = 'follower'
            suspended = False
            reset_timer = True

        if reset_timer:
            timeout = False
            reset_last_timer = datetime.utcnow()
            reset_timer = False

        elif (datetime.utcnow() - reset_last_timer).total_seconds() * 1000 > timer:
            timeout = True
            reset_last_timer = datetime.utcnow()

        lock_timer.release()
        time.sleep(0.003)


# starting threads
thread_server = Thread(target=rpc_server)
thread_client = Thread(target=rpc_client)
thread_timer = Thread(target=timer_thread)

thread_list = [thread_server, thread_client, thread_timer]
for i in thread_list:
    i.start()
