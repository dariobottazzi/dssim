import random

class Channel(object):
    """
    This is the abstraction of a communications channel. The goal is to enable the communication between the different
    processes composing the distributed system.
    """
    def __init__(self, env, sender, receiver, bandwidth):
        """
        This is the constructor of the class

        :simpy.Environment env: it makes it possible to implement delays in message communications
        :Node sender: the communication sender
        :Node receiver: the communication receiver
        :int bandwidth: channel bandwidth in Kbps
        """
        self.env = env
        self.sender = sender
        self.receiver = receiver
        self.start_time = env.now
        self.bandwidth = bandwidth * 1024 / 8 # Bytes per second

    def __repr__(self):
        return '%r -> %r' % (self.sender, self.receiver)

    def _delivery (self, msg):
        if (self.receiver.is_connected(msg.sender) and self.receiver.is_active()):
            self.receiver.msg_queue.put(msg)
            print self.env.now, "\t", self.sender, "\t->\t", self.receiver, "\t", msg
        elif not(self.receiver.is_connected(msg.sender)):
            print self.env.now, "\t", self.sender, "\t-X\t", self.receiver, "\tDROP: ", msg
        else:
            print self.env.now, "\t", self.sender, "\t-X\t", self.receiver, "\tRECIPIENT DOWN: ", msg

    def send(self, msg):
        """
        The send method makes it possible to deliver a message to the receiver. The message is simply put in
        receiver incoming message queue, and it is up to the receiver to process and indicate it to the application
        layer.

        :BaseMessage msg: the actual message to communicate.
        """
        pass


class FIFO_Channel(Channel):
    """
    The class implements the FIFO communications channel abstraction. This channel can easily model TCP links and
    guarantees order in message delivery with regards to consequent message transmissions.
    """

    def __init__(self, env, sender, receiver, bandwidth, rt_min = 10, rt_max=300):
        """
        :simpy.Environment env: it makes it possible to implement delays in message communications
        :Node sender: the communication sender
        :Node receiver: the communication receiver
        :int bandwidth: channel bandwidth in Kbps
        :int rt_min: lower-bound of the communications round trip time in milliseconds
        :int rt_max: upper-bound of the communications round trip time in milliseconds
        """
        super(FIFO_Channel, self).__init__(env, sender, receiver, bandwidth)
        self.rt_min = rt_min
        self.rt_max = rt_max

    @property
    def round_trip(self):
        return random.randrange(self.rt_min, self.rt_max) / 1000.

    def send(self, msg):
        """
        Sends the message to the receiver. It simulates the delay in message delivery by taking into account both rtt and
        the available bandwidth in message communications.

        :BasicMessage msg: the message to communicate
        """

        def _transfer():
            delay = msg.size / self.bandwidth
            delay += self.round_trip / 2
            yield self.env.timeout(delay)
            self._delivery(msg)

        self.env.process(_transfer())



class Perfect_Link_Channel (Channel):
    """
    The class implements the a non-FIFO communications channel abstraction.

    """

    def __init__(self, env, sender, receiver, bandwidth, rt_min = 10, rt_max=300, probability_delay=0.05, max_delay_infrastructure = 50):
        """
        :simpy.Environment env: it makes it possible to implement delays in message communications
        :Node sender: the communication sender
        :Node receiver: the communication receiver
        :int bandwidth: channel bandwidth in Kbps
        :int rt_min: lower-bound of the communications round trip time in milliseconds
        :int rt_max: upper-bound of the communications round trip time in milliseconds
        :real probability_delay: probability of actual message delay
        :int max_delay_infrastructure: upperbound of the delay of the infrastructure in milliseconds
        """
        super(Perfect_Link_Channel, self).__init__(env, sender, receiver, bandwidth)
        self.rt_min = rt_min
        self.rt_max = rt_max
        self.probability_delay = probability_delay
        self.max_delay_infrastructure = max_delay_infrastructure / 1000. # translate delay in seconds

    @property
    def round_trip(self):
        return random.randrange(self.rt_min, self.rt_max) / 1000.

    def send(self, msg):
        """
        Sends the message to the receiver. It simulates the delay in message delivery by taking into account both rtt and
        the available bandwidth in message communications.

        :BasicMessage msg: the message to communicate
        """

        def _transfer():
            delay = msg.size / self.bandwidth
            delay += self.round_trip / 2
            yield self.env.timeout(delay)
            self._delivery(msg)

        if (random.random() <= self.probability_delay):
            yield self.env.timeout(self.max_delay_infrastructure) # TODO: controllare che possano essere mandati altri messaggi comunque

        self.env.process(_transfer())



class Fairloss_Channel(FIFO_Channel):

    def __init__(self, env, sender, receiver, bandwidth, delivery_probability=0.99, rt_min = 10, rt_max=300):
        """
        :simpy.Environment env: it makes it possible to implement delays in message communications
        :Node sender: the communication sender
        :Node receiver: the communication receiver
        :int bandwidth: channel bandwidth in Kbps
        :float delivery_probability: message delivery probability
        :int rt_min: lower-bound of the communications round trip time in milliseconds
        :int rt_max: upper-bound of the communications round trip time in milliseconds
        """
        super(Fairloss_Channel, self).__init__(env, sender, receiver, bandwidth, rt_min, rt_max)
        self.probability = delivery_probability

    def send(self, msg):
        """
        Sends the message to the receiver. It simulates the delay in message delivery by taking into account both rtt and
        the available bandwidth in message communications.

        :BasicMessage msg: the message to communicate
        """
        run_dice = random.random()
        if (run_dice <= self.probability):
            super(Fairloss_Channel, self).send(msg)
        else:
            print "channel dropped the message"


class Loss_Repetition_Channel (FIFO_Channel):

    def __init__(self, env, sender, receiver, bandwidth, delivery_probability=0.99, max_retrasmission = 3, max_time_retrasmission = 10, rt_min = 10, rt_max=300):
        """

        :simpy.Environment env: it makes it possible to implement delays in message communications
        :Node sender: the communication sender
        :Node receiver: the communication receiver
        :int bandwidth: channel bandwidth in Kbps
        :float delivery_probability: message delivery probability
        :int max_retrasmission: max number of retransmissions of the same message
        :int max_time_retrasmission: time between retransmissions in milliseconds
        :int rt_min: lower-bound of the communications round trip time in milliseconds
        :int rt_max: upper-bound of the communications round trip time in milliseconds
        """
        super(Loss_Repetition_Channel, self).__init__(env, sender, receiver, bandwidth, delivery_probability, rt_min, rt_max)
        self.max_retrasmission = max_retrasmission
        self.max_time_retrasmission = max_time_retrasmission / 1000.

    def send(self, msg):
        """
        Sends the message to the receiver.

        :BasicMessage msg: the message to communicate
        """
        run_dice = random.random()
        number_tx = int(run_dice * self.max_retrasmission) + 1

        for i in range(number_tx):
            super(Loss_Repetition_Channel,self).send(msg)
            if (number_tx>1):
                yield self.env.timeout(self.max_time_retrasmission * random.random())

class Channel_Factory:
    def __init__(self, channel_type):
        self.channel_type = channel_type
        self.rt_min = 10
        self.rt_max = 300
        self.delivery_probability = 0.99
        self.max_retrasmission = 3
        self.max_time_retrasmission = 10
        self.probability_delay = 0.05
        self.max_delay_infrastructure = 50
        self.bandwidth = 2400 # Kbps

    def factory(self, env, sender, receiver):
        if (self.channel_type=="FIFO_Channel"):
            return FIFO_Channel(env, sender, receiver, self.bandwidth, self.rt_min, self.rt_max)
        elif (self.channel_type=="Fairloss_Channel"):
            return Fairloss_Channel (env, sender, receiver, self.bandwidth, self.delivery_probability, self.rt_min, self.rt_max)
        elif (self.channel_type=="Loss_Repetition_Channel"):
            return Loss_Repetition_Channel (env, sender, receiver, self.bandwidth, self.delivery_probability, self.max_retrasmission, self.max_time_retrasmission, self.rt_min, self.rt_max)
        elif (self.channel_type=="Perfect_Link_Channel"):
            return Perfect_Link_Channel (env, sender, receiver, self.bandwidth, self.rt_min, self.rt_max, self.probability_delay, self.max_delay_infrastructure)
