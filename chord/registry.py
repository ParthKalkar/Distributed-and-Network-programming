"""
Author - Parth Kalkar

This is the registry.py file. It is responsible to register and deregister the nodes.
Its behavior is implemented by Registry class which is a child of Thread or Process class.

"""

import threading
import random


# Registry Class
class Registry(threading.Thread):
    nodes = {}

    def __init__(self, m):
        threading.Thread.__init__(self)
        self.m = m

    # Register Function
    def register(self, port):
        if len(self.nodes) == pow(2, self.m):  # 2 ** self.m:
            return -1, "Chord is full"

        random.seed(0)

        new_id = random.randint(0, pow(2, self.m) - 1)  # 2 ** self.m - 1)
        while new_id in self.nodes:
            new_id = random.randint(0, pow(2, self.m) - 1)  # 2 ** self.m - 1)

        self.nodes[new_id] = port
        return new_id, f"The network size now is {len(self.nodes)}"

    # Deregister Function
    def deregister(self, id_):
        if id_ not in self.nodes.keys:
            return False, "no such id exists"

        self.nodes.pop(id_)
        return True, "Success"

    # Get Chord Info Function
    def get_chord_info(self):
        return self.nodes

    # Populate Finger Table Function
    def populate_finger_table(self, id_):
        def successor(node_):
            for i_ in range(int(node_) % pow(2, self.m), pow(2, self.m)):  # (2 ** self.m, 2 ** self.m):
                if i_ in self.nodes and i_ != id_:
                    return i_

        finger_table = {}
        for i in range(self.m):
            finger_table[successor(id_ + pow(2, i))] = self.nodes[successor(id_ + pow(2, i))]

        return finger_table
