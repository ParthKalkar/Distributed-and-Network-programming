"""
Author - Parth Kalkar

This is the node.py file. A usual p2p node of chord overlay. It is implemented by a Node class which is a child of
either Thread or Process class. Node when created isn’t part of chord.

"""

from multiprocessing import Process
from threading import Thread, Lock
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
import time
import zlib


class CustomXMLRPCServer(SimpleXMLRPCServer):
    def serve_forever(self):
        self.quit = 0
        while not self.quit:
            self.handle_request()


class Node(Process):
    def __init__(self, m, port, registry_ip, registry_port):
        super(Node, self).__init__()
        self.m = m
        self.finger_table, self.predecessor = None, None
        self.XmlRpc_server = None
        self.files = {}
        self.port = port
        self.registry = ServerProxy(f'http://{registry_ip}:{registry_port}')
        self.id, self.registration_message = self.registry.register(port)
        self.finger_table_lock = Lock()
        self.predecessor_lock = Lock()
        self.quit_update = False
        if self.id == -1:
            return
        self.start()

    def get_finger_table(self):
        return self.finger_table

    def quit(self):
        self.quit_update = True
        registry = self.registry.deregister(self.id)
        if not registry[0]:
            return False, f"Node {self.id} with port {self.port} isn’t part of the network"
        successor = ServerProxy(f'http://127.0.0.1:{self.finger_table[str(self.successor_id())]}')
        successor.quit_notification_to_successor(self.predecessor, self.files)
        ServerProxy(
            f'http://127.0.0.1:{self.finger_table[str(self.predecessor[0])]}').quit_notification_to_predecessor()
        return registry

    def exit_process(self):
        if self.XmlRpc_server is not None:
            self.XmlRpc_server.quit = 1

    def update_finger_table(self):
        while True:
            time.sleep(1)
            if self.quit_update:
                break
            self.predecessor_lock.acquire()
            self.finger_table_lock.acquire()
            self.finger_table, self.predecessor = self.registry.populate_finger_table(self.id)
            self.predecessor_lock.release()
            self.finger_table_lock.release()

    def savefile(self, filename):
        hash_value = zlib.adler32(filename.encode())
        target_id = hash_value % 2 ** self.m

        return self.file_lookup(target_id, filename)

    def successor_id(self):
        keys = list(map(int, self.finger_table.keys()))
        for i in range(int(self.id) + 1, 2 ** self.m):
            if i in keys:
                return i
        return min(map(int, self.finger_table.keys()))

    def farthest_node(self, target_id):
        index = -1
        sorted_keys = sorted(map(int, self.finger_table.keys()))
        while sorted_keys[index] <= target_id:
            index += 1
            if index == len(sorted_keys):
                break
        return sorted_keys[index - 1]

    def file_lookup(self, target_id, filename):
        if int(self.predecessor[0]) < target_id <= int(self.id) or (
                int(self.predecessor[0]) > int(self.id) >= target_id):
            if self.files.get(filename):
                return False, f"{filename} already exists in Node {self.id}"
            self.files[filename] = True
            return True, f"{filename} saved in Node {self.id}"
        if int(self.id) < target_id <= int(self.successor_id()):
            print(f"Node {self.id} passed request to node {self.successor_id()}")
            successor_rpc = ServerProxy(f'http://127.0.0.1:{self.finger_table[str(self.successor_id())]}')
            return successor_rpc.savefile(filename)
        farthest = self.farthest_node(target_id)
        print(f"Node {self.id} passed request to node {farthest}")
        return ServerProxy(f'http://127.0.0.1:{self.finger_table[str(farthest)]}').savefile(filename)

    def getfile(self, filename):
        hash_value = zlib.adler32(filename.encode())
        target = hash_value % 2 ** self.m
        if int(self.predecessor[0]) < target <= int(self.id) or (
                int(self.predecessor[0]) > int(self.id) >= target):
            if self.files.get(filename):
                return True, f"Node {self.id} has {filename}"
            return False, f"Node {self.id} doesn’t have {filename}"
        if int(self.id) < target <= self.successor_id():
            print(f"Node {self.id} passed request to node {self.successor_id()}")
            successor_rpc = ServerProxy(f'http://127.0.0.1:{self.finger_table[str(self.successor_id())]}')
            return successor_rpc.getfile(filename)
        farthest = self.farthest_node(target)
        print(f"Node {self.id} passed request to node {farthest}")
        return ServerProxy(f'http://127.0.0.1:{self.finger_table[str(farthest)]}').getfile(filename)

    def quit_notification_successor(self, predecessor, files):
        self.files.update(files)
        self.predecessor_lock.acquire()
        self.predecessor = predecessor
        self.predecessor_lock.release()
        return True

    def quit_notification_predecessor(self):
        self.finger_table_lock.acquire()
        self.predecessor_lock.acquire()
        self.finger_table, self.predecessor = self.registry.populate_finger_table(self.id)
        self.predecessor_lock.release()
        self.finger_table_lock.release()
        return True

    def run(self):
        finger_table_updater = Thread(target=self.update_finger_table, daemon=True)
        finger_table_updater.start()
        try:
            with SimpleXMLRPCServer(('127.0.0.1', self.port), logRequests=False) as server:
                self.XmlRpc_server = server
                server.register_introspection_functions()
                funcs = [self.get_finger_table, self.quit, self.savefile, self.getfile, self.quit_notification_successor, self.quit_notification_predecessor]
                for i in funcs:
                    server.register_function(i)
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    print(f"Exiting {self.name} Process ...")
                    server.server_close()
                    exit(0)
                print("Exiting Node server ...")
        except Exception as e:
            exit(1)
