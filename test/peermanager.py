from simul.messages import BaseMessage
from simul.services import BaseService

import random


###### Messages ################


class Ping(BaseMessage):
    def __init__(self, sender):
        super(Ping, self).__init__(sender)
        self.sender = sender

    def __repr__(self):
        return "Ping"

class Pong(BaseMessage):
    def __init__(self, sender):
        super(Pong, self).__init__(sender)
        self.sender = sender

    def __repr__(self):
        return "Pong"

###### Services ################

class Test_service (BaseService):

    def __init__(self, env, peer):
        self.peer = peer
        self.action = env.process(self.run())

    def __repr__(self):
        return "Test_service(%s)" % self.peer.name

    @property
    def env(self):
        return self.peer.env

    def handle_message(self, peer, msg):
        if isinstance(msg, Ping):
            print self.env.now, self.peer.name, " received ping from ", msg.sender
            self.env.timeout(random.random())

            print self.env.now, self.peer.name, " sent pong to ", msg.sender
            self.peer.send(msg.sender, Pong(self.peer))
        elif isinstance(msg, Pong):
            print self.env.now, self.peer.name, " recived pong from ", msg.sender
        else:
            print self.env.now, self.peer.name, "drops the message from ", msg.sender, " because its type is unknown"


    def execution_time(self):
        return random.randint(1, 10) / 10. + 1  # time [1, 2]

    def run(self):
        while True:
            # send a message including the logical time
            keys = self.peer.connections.keys()
            for i in keys:
                if self.peer.is_active():
                    print self.env.now, self.peer.name, " sent ping to ", i
                    self.peer.send(i, Ping(self.peer))
            etime = 2#self.execution_time() # passa la simulazione al prossimo
            yield self.env.timeout(etime)