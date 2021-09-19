"""
Author - Parth Kalkar

This is the node.py file. A usual p2p node of chord overlay. It is implemented by a Node class which is a child of
either Thread or Process class. Node when created isn’t part of chord.

"""
import threading
import time


# Node Class
class Node(threading.Thread):
    finger_table = {}

    def __init__(self, port, registry_thread):
        threading.Thread.__init__(self)
        self.port = port
        self.registry_thread = registry_thread

    def run(self):
        id_content = self.registry_thread.register(self.port)
        time.sleep(1)
        self.finger_table = self.registry_thread.populate_finger_table(id_content[0])

    def get_finger_table(self):
        return self.finger_table

    def quit(self):
        return self.registry_thread.deregister()
