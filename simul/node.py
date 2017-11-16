import simpy
from messages import Message, NetworkMessage
from services import BaseService

class Node(object):

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
        assert isinstance(other, Node)
        if not self.is_connected(other):
            print self.env.now, "\t", self, "\tconnected to", other
            self.connections[other] = self.channel_factory.factory(self.env, self, other)
            if not other.is_connected(self):
                other.connect(self)

    def disconnect(self, other):
        assert isinstance(other, Node)
        if self.is_connected(other):
            print self.env.now, "\t", self, "\tdisconnected from", other
            del self.connections[other]
            if other.is_connected(self):
                other.disconnect(self)

    def is_connected(self, other):
        assert isinstance(other, Node)
        return other in self.connections

    def is_active(self):
        return self.active

    def is_disconnected (self):
        return not(bool(self.connections))

    def receive(self, msg):
        assert isinstance(msg, Message)

        if (self.active == True):    # propagate the message only if the node is active
            for s in self.services:  # TODO: consider the implementation of a registration mechanism to reduce overhead by providing messages only to services which are able to handle them
                assert isinstance(s, BaseService)
                s.handle_message(msg)

    def send(self, receiver, msg):
        # fire and forget
        assert isinstance(msg, NetworkMessage)
        assert isinstance(receiver, Node)

        if (self.active == True):   # send the message only if the node is active
            assert msg.sender == self
            self.connections[receiver].send(msg)

    def indicate (self, msg):
        # this method is similar to send but it is conceived for communications between services in the same node
        assert isinstance(msg, Message)

        if (self.active == True):
            self.msg_queue.put(msg)

    def broadcast(self, msg):
        assert isinstance(msg, NetworkMessage)

        if (self.active == True):  # send the message only if the node is active
            for other in self.connections:
                self.send(other, msg)

    def run(self):
        while True:
            msg = yield self.msg_queue.get() # check network for new messages
            self.receive(msg)

