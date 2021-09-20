"""
Author - Parth Kalkar

This is the registry.py file. It is responsible to register and deregister the nodes.
Its behavior is implemented by Registry class which is a child of Thread or Process class.

"""

from xmlrpc.server import SimpleXMLRPCServer
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
        if len(self.nodes) == pow(2, self.m):
            return -1, "Chord is full"

        random.seed(0)

        generate_id_ = random.randint(0, pow(2, self.m) - 1)
        while str(generate_id_) in self.nodes:
            generate_id_ = random.randint(0, pow(2, self.m) - 1)

        self.nodes[str(generate_id_)] = port
        return generate_id_, f"The network size now is {len(self.nodes)}"

    # Deregister Function
    def deregister(self, id_):
        if str(id_) not in self.nodes:
            return False, "no such id exists"

        self.nodes.pop(str(id_))
        return True, "Success"

    # Chord Info Function
    def get_chord_info(self):
        return self.nodes

    # Populate Finger Table
    def populate_finger_table(self, id_):
        def neighbour_node(num):
            for i_ in range(int(num) % pow(2, self.m), pow(2, self.m)):
                if str(i_) in self.nodes and i_ != id_:
                    return i_

        finger_table = {}
        for i in range(self.m):
            value = neighbour_node(id_ + pow(2, i))
            finger_table[str(value)] = self.nodes[str(value)]

        return finger_table

    # Run function
    def run(self):
        def register(port):
            return self.register(port)

        def deregister(id_):
            return self.deregister(id_)

        def get_chord_info():
            return self.get_chord_info()

        def populate_finger_table(id_):
            return self.populate_finger_table(id_)

        with SimpleXMLRPCServer(("127.0.0.1", 8081)) as server:
            funcs = [register, deregister, get_chord_info, populate_finger_table]
            for i in funcs:
                server.register_function(i)
            server.serve_forever()
