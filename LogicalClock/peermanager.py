# definition of the protocol to simulate

from simul.services import BaseService
from simul.messages import BaseMessage

import random


###### Messages ################


class MessageTime(BaseMessage):
    def __init__(self, sender, logical_time):
        super(MessageTime, self).__init__(sender)
        self.sender = sender
        self.data = logical_time


###### Services ################

class Lamport_clock_service(BaseService):

    def __init__(self, env, peer):
        self.peer = peer
        self.clock = 0
        self.action = env.process(self.run())

    def __repr__(self):
        return "Lamport_clock_service(%s)" % self.peer.name

    @property
    def env(self):
        return self.peer.env

    def handle_message(self, peer, msg):
        if isinstance(msg, MessageTime):
            print self.env.now, self.peer.name, " recived msg from ", msg.sender, " with clock ", msg.data
            if (msg.data > self.clock):
                print self.env.now, self.peer.name, " updates clock from ", self.clock, " to ", msg.data
                self.clock = msg.data + 1
            else:
                print self.env.now, self.peer.name, "drops the message from ", msg.sender, " because recived clock is late "


    def execution_time(self):
        return random.randint(1, 10) / 10. + 1  # time [1, 2]

    def run(self):
        while True:
            # do stuff for some random amount of time
            self.clock = self.clock + 1
            print self.env.now, "\t", self.clock, "\t", self.peer.name
            etime = self.execution_time()
            yield self.env.timeout(etime)

            # send a message including the logical time
            keys = self.peer.connections.keys()
            selected = int(random.random() * len(keys))
            self.clock = self.clock + 1
            print self.env.now, "\t", self.clock, "\t", self.peer.name
            self.peer.send(keys[selected], MessageTime(self.peer, self.clock))
            etime = self.execution_time() # passa la simulazione al prossimo
            yield self.env.timeout(etime)