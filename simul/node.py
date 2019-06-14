import simpy
from messages import Message, NetworkMessage
from services import BaseService


############################################################################################################
##
## Node class definition
##
############################################################################################################


class Node(object):
    """The Node class represents a network node.The Node is an active entity into the system and it is 
    characterised by several attributes.
    """

    def __init__(self, name,  env, channel_factory):
        """
        The constructor for the Node class. Requires to specify the following parameters

        :str name: the node name
        :simpy.Environemnt env: the simulation environemnt
        :Channel_Factory channel_factory: the channel factory that makes it possible to define the channel 
        model
        """
        self.name = name
        self.env = env
        self.msg_queue = simpy.Store(env)
        self.connections = dict()
        self.active = True
        self.services = []
        self.channel_factory = channel_factory
        env.process(self.run())

    def __repr__(self):
        """
        :str name : returns the name of the node
        """
        return self.name


    def connect(self, other):
        """
        makes it possible to setup a connection between nodes

        :Node other: the node to connect with
        """
        assert isinstance(other, Node)
        if not self.is_connected(other):
            self.connections[other] = self.channel_factory.factory(self.env, self, other)

            if not other.is_connected(self):
                other.connect(self)

    def disconnect(self, other):
        """
        makes it possible to disconnect nodes

        :Node other: the node to disconnect from
        """
        assert isinstance(other, Node)
        if self.is_connected(other):
            del self.connections[other]

            if other.is_connected(self):
                other.disconnect(self)

    def is_connected(self, other):
        """
        Makes it possible to verify whether two nodes are connected. The method returns true if two nodes, 
        are connected. False otherwise.

        :Node other: the node wrt the connection should be verified
        """
        assert isinstance(other, Node)
        return other in self.connections

    def is_active(self):
        """
        The method returns true if the node is active, and false if the node is not active.
        """
        return self.active

    def is_disconnected (self):
        """
        The method returns true is the node has no network connections. False otherwise.
        """
        return not(bool(self.connections))

    def receive(self, msg):
        """
        The method simulates a received message. The received message is forwarded to all services running 
        on top of the node.

        :Message msg: received message
        """
        assert isinstance(msg, Message)

        if (self.active == True):    # propagate the message only if the node is active
            for s in self.services:  # TODO: consider the implementation of a registration mechanism to reduce overhead by providing messages only to services which are able to handle them
                assert isinstance(s, BaseService)
                s.handle_message(msg)

    def send(self, receiver, msg):
        """
        The method is to send a message to a specified recipient

        :Node receiver: recipient of the message
        :Message msg: message to be sent
        """
        # fire and forget
        assert isinstance(msg, NetworkMessage)
        assert isinstance(receiver, Node)

        if (self.active == True):   # send the message only if the node is active
            assert msg.sender == self
            self.connections[receiver].send(msg)

    def indicate (self, msg):
        """
        this method is similar to send but enables the communication between services running on the same 
        node

        :Message msg: message to be delivered
        """
        assert isinstance(msg, Message)

        if (self.active == True):
            self.msg_queue.put(msg)

    def run(self):
        while True:
            msg = yield self.msg_queue.get() # check network for new messages
            self.receive(msg)


"""
NOTES. At present time when the node receives a message it forward it to all services that are active into 
the node. This mechanism is rather espancive in terms of computational cost. As a consequence it is 
advisable to avoid the problem by considering to deliver the message only to the expected service.

A mitigation could be deliverng the message as long as a service consume it.
"""




"""
REMOVED BROADCAST.
    def broadcast(self, msg):
        assert isinstance(msg, NetworkMessage)

        if (self.active == True):  # send the message only if the node is active
            for other in self.connections:
                self.send(other, msg)
"""
