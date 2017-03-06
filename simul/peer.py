import simpy
import random
from messages import BaseMessage

class Channel(object):
    def __init__(self, env, sender, receiver):
        self.env = env
        self.sender = sender
        self.receiver = receiver
        self.start_time = env.now

    def __repr__(self):
        return '<Connection %r -> %r>' % (self.sender, self.receiver)

    def delivery (self, msg, connect=False):
        if self.receiver.is_connected(msg.sender) or connect:
            self.receiver.msg_queue.put(msg)

    def send(self, msg, connect=False):
        pass


class FIFO_Channel(Channel):

    def __init__(self, env, sender, receiver, rt_min = 10, rt_max=300):
        super(FIFO_Channel, self).__init__(env, sender, receiver)
        self.rt_min = rt_min
        self.rt_max = rt_max

    @property
    def round_trip(self):
        # basically backbone latency
        # evenly distributed pseudo random round trip times
        return (self.rt_min + (id(self.sender) + id(self.receiver)) % (self.rt_max-self.rt_min)) / 1000.

    @property
    def bandwidth(self):
        return min(self.sender.bandwidth_ul, self.receiver.bandwidth_dl)

    def send(self, msg, connect=False):

        def _transfer():
            bytes = msg.size
            delay = bytes / self.sender.bandwidth_ul
            delay += bytes / self.receiver.bandwidth_dl
            delay += self.round_trip / 2
            yield self.env.timeout(delay)
            self.delivery(msg)

        self.env.process(_transfer())



class Perfect_Link_Channel (Channel): # delay make the channel perfect in delivery, but do not guarantee FIFO delivery

    def __init__(self, env, sender, receiver, rt_min = 10, rt_max=300, probability_delay=0.05, max_delay_infrastructure = 50):
        super(Perfect_Link_Channel, self).__init__(env, sender, receiver)
        self.rt_min = rt_min
        self.rt_max = rt_max
        self.probability_delay = probability_delay
        self.max_delay_infrastructure = max_delay_infrastructure

    @property
    def round_trip(self):
        # basically backbone latency
        # evenly distributed pseudo random round trip times
        return (self.rt_min + (id(self.sender) + id(self.receiver)) % (self.rt_max-self.rt_min)) / 1000.

    @property
    def bandwidth(self):
        return min(self.sender.bandwidth_ul, self.receiver.bandwidth_dl)

    def send(self, msg, connect=False):

        def _transfer():
            bytes = msg.size
            delay = bytes / self.sender.bandwidth_ul
            delay += bytes / self.receiver.bandwidth_dl
            delay += self.round_trip / 2
            yield self.env.timeout(delay)
            self.delivery(msg)

        if (random.random()<self.probability_delay):
            yield self.env.timeout(self.max_delay_infrastructure * random.random())

        self.env.process(_transfer())



class Fairloss_Channel(FIFO_Channel):

    def __init__(self, env, sender, receiver, delivery_probability=0.99, rt_min = 10, rt_max=300):
        super(Fairloss_Channel, self).__init__(env, sender, receiver, rt_min, rt_max)
        self.probability = delivery_probability

    def send(self, msg, connect=False):
        run_dice = random.random()
        if (run_dice <= self.probability):
            super(Fairloss_Channel, self).send(msg, connect)
        else:
            print "channel dropped the message"


class Loss_Repetition_Channel (FIFO_Channel):

    def __init__(self, env, sender, receiver, delivery_probability=0.99, max_retrasmission = 3, max_time_retrasmission = 10, rt_min = 10, rt_max=300):
        super(Loss_Repetition_Channel, self).__init__(env, sender, receiver, delivery_probability, rt_min, rt_max)
        self.max_retrasmission = max_retrasmission
        self.max_time_retrasmission = max_time_retrasmission

    def send(self, msg, connect=False):
        run_dice = random.random()
        number_tx = int(run_dice * self.max_retrasmission) + 1

        for i in range(number_tx):
            super(Loss_Repetition_Channel,self).send(msg, connect)
            if (number_tx>1):
                yield self.env.timeout(self.max_time_retrasmission * random.random())


class Channel_Factory:
    def __init__(self, channel_type):
        self.channel_type = channel_type
        self.rt_min = 10
        self.rt_max = 300
        self.delivery_probability = 0.99

    def factory(self, env, sender, receiver):
        if (self.channel_type=="FIFO_Channel"):
            return FIFO_Channel(env, sender, receiver)
        elif (self.channel_type=="Fairloss_Channel"):
            return Fairloss_Channel (env, sender, receiver)
        elif (self.channel_type=="Loss_Repetition_Channel"):
            return Loss_Repetition_Channel (env, sender, receiver)
        elif (self.channel_type=="Perfect_Link_Channel"):
            return Perfect_Link_Channel (env, sender, receiver)

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
        self.services = [] # Service.handle_message(self, msg) called on message
        self.disconnect_callbacks = []
        self.channel_factory = channel_factory
        env.process(self.run())

    def __repr__(self):
        #return '<%s %s>' % (self.__class__.__name__, self.name)
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

