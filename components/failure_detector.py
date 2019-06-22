from simul.messages import NetworkMessage, Message
from simul.services import BaseService
from simul.disruptions import Node_Down, Node_Running

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

class Availability_Internal_Message(Message):
    def __init__(self, data=None):
        super(Availability_Internal_Message, self).__init__(data)

    def __repr__(self):
        return "Availability_Internal_Message"

################ Services ################

class Perfect_Failure_Detector (BaseService):
    """The Perfect Failure Detectors assumes to operate in a fail-stop model"""

    def __init__(self, env, node, response_threshold, epoch_threshold):
        self.node = node # reference to the node
        self.action = env.process(self.run())
        self.connections = node.connections # list of available connections
        self.response_threshold = response_threshold # expected peer response time
        self.active = {} # this is the list of currently active and connected processors in the system.
        self.received = {}
        self.epoch_threshold = epoch_threshold
        for i in self.node.connections.keys():
            self.received[i] = False

    def __repr__(self):
        return "Perfect Failure Detector(%s)" % self.node.name

    @property
    def env(self):
        return self.node.env

    def execution_time(self):
        return random.uniform(0,0.300)

    def handle_message(self, msg):
        if isinstance(msg, HeartbeatReqMessage):
            self.log("%.4f" % self.env.now+" "+self.node.name+" received heartbeat request from "+ msg.sender.name)
            self.env.timeout(self.execution_time())
            self.log("%.4f" % self.env.now+" "+self.node.name+" sent heartbeat response to "+ msg.sender.name)
            self.node.send(msg.sender, HeartbeatRespMessage(self.node))

        elif isinstance(msg, HeartbeatRespMessage):
            self.log("%.4f" % self.env.now + " "+self.node.name+" received heartbeat response from "+ msg.sender.name)
            if (self.active[msg.sender]): # reset of the timer if it is active. When we received a message from a node declared down we skip it
                self.received[msg.sender] = True

    def run(self):

        yield self.env.timeout(random.uniform(0, 0.500)) # to avoid synch between entities

        for i in self.connections.keys():
            self.active[i] = True # the i-th processor is active.


        while True:
            keys = self.active.keys() # set of active nodes in the system

            for i in keys:
                self.received[i] = False

            for i in keys:
                self.log("%.4f" % self.env.now + " " + self.node.name + " sent heartbeat to " + i.name)
                self.node.send(i, HeartbeatReqMessage(self.node))
                yield self.env.timeout(self.execution_time())

            yield self.env.timeout(self.response_threshold)


            for i in keys:
                if (self.received[i]==False):
                    self.active[i] = False
                    self.log("%.4f" % self.env.now + " " + i.name + " is down")

            self.log("%.4f" % self.env.now + "\t" + self.node.name+ "\t" +str(self.received)) # TODO: mettere a posto visualizzazione piu compatta

            avail_nodes = []
            for j in self.received.keys():
                if self.received[j] == True:
                    avail_nodes.append(j)

            self.node.indicate(Availability_Internal_Message(avail_nodes))

            #self.node.indicate(Availability_Internal_Message(self.received.keys()))

            yield self.env.timeout(self.epoch_threshold)





class Eventually_Perfect_Failure_Detector (BaseService):
    """The Eventually Perfect Failure Detector assumes to operate in a fail-recovery model"""

    def __init__(self, env, node, response_threshold, epoch_threshold):
        self.node = node # reference to the node
        self.action = env.process(self.run())
        self.connections = node.connections # list of available connections
        self.active = {} # this is the list of currently active and connected processors in the system.
        self.suspected = {}
        for i in self.node.connections.keys():
            self.suspected[i] = True
            self.active [i] = False

        self.response_threshold = response_threshold # expected peer response time
        self.epoch_threshold = epoch_threshold


    def __repr__(self):
        return "Eventually_Perfect_Failure_Detector (%s)" % self.node.name

    @property
    def env(self):
        return self.node.env

    def execution_time(self):
        return random.uniform(0,0.300)

    def handle_message(self, msg):
        if isinstance(msg, HeartbeatReqMessage):
            self.log("%.4f" % self.env.now+" "+self.node.name+" received heartbeat request from "+ msg.sender.name)
            self.env.timeout(self.execution_time())
            self.log("%.4f" % self.env.now+" "+self.node.name+" sent heartbeat response to "+ msg.sender.name)
            self.node.send(msg.sender, HeartbeatRespMessage(self.node))
            self.env.timeout(self.execution_time())

        elif isinstance(msg, HeartbeatRespMessage):
            self.log("%.4f" % self.env.now + " "+self.node.name+" received heartbeat response from "+ msg.sender.name)
            self.suspected[msg.sender] = False


    def run(self):

        yield self.env.timeout(random.uniform(0, 0.500)) # to avoid synch between entities

        keys = []

        for i in self.connections.keys():
            self.active[i] = True # the i-th processor is active.
            keys.append(i)

        #keys = ['P0', 'P1', 'P2', 'P3']

        while True:

            for i in keys:
                self.suspected[i] = True
                self.active[i] = False


            for i in keys:
                self.log("%.4f" % self.env.now + " " + self.node.name + " sent heartbeat to " + i.name)
                self.node.send(i, HeartbeatReqMessage(self.node))
                yield self.env.timeout(self.execution_time())

            yield self.env.timeout(self.response_threshold)

            for i in keys:
                if (self.suspected[i]==True):
                    self.active[i] = False
                    self.log("%.4f" % self.env.now + " " + i.name + " is suspected to be down")
                else:
                    self.active[i] = True

            self.log("%.4f" % self.env.now + "\t" + self.node.name+ "\t" +str(self.suspected))

            avail_nodes = []
            for j in self.active.keys():
                if self.active[j] == True:
                    avail_nodes.append(j)

            self.node.indicate(Availability_Internal_Message(avail_nodes))

            yield self.env.timeout(self.epoch_threshold)



#TODO: mettere la stampa delle cose nell'app failure detection e passare nel messaggio solo l'indicazione dei nodi disponibili.
#TODO: usare il messaggio di disponibilita' per notificare al leader election module come funzionano le cose.
#TODO: nel messaggio devono essere presenti tutti i nodi disponibili
