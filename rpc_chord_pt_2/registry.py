"""
Author - Parth Kalkar

This is the registry.py file. It is responsible to register and deregister the nodes.
Its behavior is implemented by Registry class which is a child of Thread or Process class.

"""
from multiprocessing import Process
from xmlrpc.server import SimpleXMLRPCServer
import random
import bisect


class CustomXMLRPCServer(SimpleXMLRPCServer):
    def serve_forever(self):
        self.quit = 0
        while not self.quit:
            self.handle_request()


def successor_(id_, sorted_ids):
    try:
        return sorted_ids[bisect.bisect_left(sorted_ids, id_)]
    except IndexError:
        return sorted_ids[0]


def predecessor_(id_, sorted_ids):
    try:
        return sorted_ids[bisect.bisect_left(sorted_ids, id_) - 1]
    except IndexError:
        return sorted_ids[-1]


class Registry(Process):
    def __init__(self, m, ip, port):
        super(Registry, self).__init__()
        self.ports = {}
        self.m = m
        self.ip_address = ip
        self.port = port
        self.xmlrpc_server = None
        self.start()

    def register(self, port):
        if len(self.ports) == 2 ** self.m:
            return -1, "Chord is full."
        id_ = str(random.randint(0, 2 ** self.m - 1))
        while id_ in self.ports:
            id_ = str(random.randint(0, 2 ** self.m - 1))
        self.ports[str(id_)] = port
        return id_, f"New chord size : {len(self.ports)}"

    def deregister(self, id_):
        id_ = str(id_)
        if self.ports.get(id_) is None:
            return False, f"Node {id_} isn’t part of the network"
        port = self.ports[id_]
        self.ports.pop(str(id_), None)
        return True, f"Node {id_}  with  port  {port}  was successfully removed"

    def get_chord_info(self):
        return self.ports

    def populate_finger_table(self, id_):
        id_ = str(id_)
        finger_table = {}
        sorted_ids = sorted(map(int, self.ports.keys()))
        for i in range(1, self.m + 1):
            successor = successor_((int(id_) + 2 ** (i - 1)) % 2 ** self.m, sorted_ids)
            finger_table[str(successor)] = self.ports[str(successor)]
        predecessor = str(predecessor_(int(id_), sorted_ids))
        return finger_table, (predecessor, self.ports[predecessor])

    def exit_process(self):
        if self.xmlrpc_server is not None:
            self.xmlrpc_server.quit = 1

    def run(self):
        random.seed(0)
        try:
            with CustomXMLRPCServer((self.ip_address, self.port), logRequests=False) as server:
                self.xmlrpc_server = server
                server.register_introspection_functions()
                funcs = [self.register, self.deregister, self.get_chord_info, self.populate_finger_table]
                for i in funcs:
                    server.register_function(i)
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    print("Exiting Registry Process ...")
                    exit(0)
        except Exception as e:
            exit(1)
