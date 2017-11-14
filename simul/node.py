import simpy
from messages import BaseMessage
from services import BaseService

class Node(object): # TODO: enable verbose logging con i dettalgi di basso livello

    def __init__(self, name,  env, channel_factory):
        self.name = name
        self.env = env
        self.msg_queue = simpy.Store(env)
        self.connections = dict()
        self.active = True
        self.services = []
        self.channel_factory = channel_factory
        env.process(self.run())
        print self.env.now, "\tnode ", self.name, "\tcreated"

    def __repr__(self):
        return self.name


    def connect(self, other):
        if not self.is_connected(other):
            print self.env.now, "\t", self, "\tconnected to", other
            self.connections[other] = self.channel_factory.factory(self.env, self, other)
            if not other.is_connected(self):
                other.connect(self)

    def disconnect(self, other):
        if self.is_connected(other):
            print self.env.now, "\t", self, "\tdisconnected from", other
            del self.connections[other]
            if other.is_connected(self):
                other.disconnect(self)

    def is_connected(self, other):
        return other in self.connections

    def is_active(self):
        return self.active

    def is_disconnected (self):
        return not(bool(self.connections))

    def receive(self, msg):
        assert isinstance(msg, BaseMessage)

        if (self.active == True):    # propagate the message only if the node is active
            for s in self.services:
                assert isinstance(s, BaseService)
                s.handle_message(self, msg)

    def send(self, receiver, msg):
        # fire and forget
        if (self.active == True):   # send the message only if the node is active
            assert msg.sender == self
            self.connections[receiver].send(msg)

    def broadcast(self, msg):
        if (self.active == True):  # send the message only if the node is active
            for other in self.connections:
                self.send(other, msg)

    def run(self):
        while True:
            msg = yield self.msg_queue.get() # check network for new messages
            self.receive(msg)

