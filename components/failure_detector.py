from simul.messages import NetworkMessage, Message
from simul.services import BaseService

import random

################ Messages ################

class HeartbeatReqMessage(NetworkMessage):
    """this class represents the Heartbeat Request Message"""
    def __init__(self, sender):
        super(HeartbeatReqMessage, self).__init__(sender)
        self.sender = sender

    def __repr__(self):
        return "Heartbeat_Request"

class HeartbeatRespMessage(NetworkMessage):
    """this class represents the Heartbeat Response Message"""
    def __init__(self, sender):
        super(HeartbeatRespMessage, self).__init__(sender)
        self.sender = sender

    def __repr__(self):
        return "Heartbeat_Response"

class Avail_Internal_Message(Message):
    def __init__(self, data=None):
        super(Avail_Internal_Message, self).__init__(data)

    def __repr__(self):
        return "Avail_Internal_Message"

################ Services ################

class Perfect_Failure_Detector (BaseService):
    """The Perfect Failure Detectors assumes to operate in a fail-stop model"""

    def __init__(self, env, node, response_threshold):
        self.node = node # reference to the node
        self.action = env.process(self.run())
        self.connections = node.connections # list of available connections
        self.response_threshold = response_threshold # expected peer response time
        self.active = {} # this is the list of currently active and connected processors in the system.
        self.received = {}
        for i in self.node.connections.keys():
            self.received[i] = False

    def __repr__(self):
        return "Perfect Failure Detector(%s)" % self.node.name

    @property
    def env(self):
        return self.node.env

    def execution_time(self):
        return random.uniform(0,1)

    def handle_message(self, msg):
        if isinstance(msg, HeartbeatReqMessage):
            self.log(str(self.env.now)+" "+self.node.name+" received heartbeat request from "+ msg.sender.name)
            self.env.timeout(self.execution_time())
            self.log(str(self.env.now)+" "+self.node.name+" sent heartbeat response to "+ msg.sender.name)
            self.node.send(msg.sender, HeartbeatRespMessage(self.node))

        elif isinstance(msg, HeartbeatRespMessage):
            self.log(str(self.env.now) + " "+self.node.name+" received heartbeat response from "+ msg.sender.name)
            if (self.active[msg.sender]): # reset of the timer if it is active. When we received a message from a node declared down we skip it
                self.received[msg.sender] = True
                self.node.indicate(Avail_Internal_Message(str(self.env.now) + "\t" + self.node.name + "\t" + str(self.active)))

    def run(self):

        yield self.env.timeout(random.uniform(0, 3)) # to avoid synch between entities

        for i in self.connections.keys():
            self.active[i] = True # the i-th processor is active.


        while True:
            keys = self.active.keys() # set of active nodes in the system

            for i in keys:
                self.received[i] = False

            for i in keys:
                self.log(str(self.env.now) + " " + self.node.name + " sent heartbeat to " + i.name)
                self.node.send(i, HeartbeatReqMessage(self.node))
                yield self.env.timeout(self.execution_time())

            yield self.env.timeout(self.response_threshold)

            for i in keys:
                if (not(self.received[i])):
                    self.active[i] = False

            yield self.env.timeout(random.uniform(0, 1))


class App_Failure_Detector (BaseService):

    def handle_message(self, msg):
        if isinstance(msg, Avail_Internal_Message):
            print str(msg.data)
