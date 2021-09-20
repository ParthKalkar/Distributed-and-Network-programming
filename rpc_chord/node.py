"""
Author - Parth Kalkar

This is the node.py file. A usual p2p node of chord overlay. It is implemented by a Node class which is a child of
either Thread or Process class. Node when created isn’t part of chord.

"""

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
import threading
import time


# Class Node
class Node(threading.Thread):
    finger_table = {}

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

    # Quit Function
    def quit(self):
        with ServerProxy(f"http://127.0.0.1:{8081}/") as proxy:
            return proxy.deregister(proxy.register(self.port)[0])

    # Finger Table Function
    def get_finger_table(self):
        with ServerProxy(f"http://127.0.0.1:{8081}/") as proxy:
            return proxy.populate_finger_table(proxy.register(self.port)[0])

    # Run Action
    def run(self):
        with ServerProxy(f"http://127.0.0.1:{8081}/") as proxy:
            time.sleep(1)
            proxy.populate_finger_table(proxy.register(self.port)[0])

        with SimpleXMLRPCServer(("127.0.0.1", self.port)) as server:
            def quit_():
                return self.quit()

            def get_finger_table():
                return self.get_finger_table()

            funcs = [get_finger_table, quit_]
            for i in funcs:
                server.register_function(i)
            server.serve_forever()
