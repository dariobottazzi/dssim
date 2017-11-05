import simpy
from messages import BaseMessage


class BaseService(object):
    """
    Added to Peers to provide services like
    - connection management
    - monitoring
    - working on tasks

    """
    def handle_message(self, receiving_peer, msg):
        "this callable is added as a listener to Peer.listeners"
        pass

KBit = 1024 / 8

class Peer(object):

    bandwidth_ul = 2400 * KBit
    bandwidth_dl = 16000 * KBit

    def __init__(self, name,  env, channel_factory):
        self.name = name
        self.env = env
        self.msg_queue = simpy.Store(env)
        self.connections = dict()
        self.active = True
        self.services = []
        self.disconnect_callbacks = []
        self.channel_factory = channel_factory
        env.process(self.run())

    def __repr__(self):
        return self.name

    def connect(self, other):
        if not self.is_connected(other):
            print self.env.now,
            print " %r connecting to %r" % (self, other)
            self.connections[other] = self.channel_factory.factory(self.env, self, other)
            if not other.is_connected(self):
                other.connect(self)

    def disconnect(self, other):
        if self.is_connected(other):
            print self.env.now,
            print " %r disconnecting from %r" % (self, other)
            del self.connections[other]
            if other.is_connected(self):
                other.disconnect(self)
            for cb in self.disconnect_callbacks:
                cb(self, other)

    def is_connected(self, other):
        return other in self.connections

    def receive(self, msg):
        #print self, 'received', msg
        assert isinstance(msg, BaseMessage)

        if (self.active == True):    # propagate the message only if the peer is active
            for s in self.services:
                assert isinstance(s, BaseService)
                s.handle_message(self, msg)

    def send(self, receiver, msg):
        # fire and forget
        if (self.active == True):   # send the message only if the peer is active
            assert msg.sender == self
            self.connections[receiver].send(msg)

    def broadcast(self, msg):
        if (self.active == True):  # send the message only if the peer is active
            for other in self.connections:
                self.send(other, msg)

    def run(self):
        while True:
            # check network for new messages
            #print self, 'waiting for message'
            msg = yield self.msg_queue.get()
            self.receive(msg)

