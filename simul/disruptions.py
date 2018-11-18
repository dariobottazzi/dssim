
from services import BaseService
import simpy
from messages import Message
from node import Node


###################################################### Messages

class Node_Down (Message):

    def __repr__(self):
        return "Node is Down"

class Node_Running (Message):

    def __repr__(self):
        return "Node is Running"


###################################################### Disruption


class BaseDisruption(BaseService):   # TODO: controllare le disruption e verificare che le cose vadano come atteso
    """
    the class changes on-line behaviour of the node at regular times
    """
    is_disrupted = True
    verbose = True

    def __init__(self, env, node, time):
        self.env = env
        self.node = node
        self.env.process(self.run())
        self.time = time # secs (time between failures)

        assert isinstance(env, simpy.Environment)
        assert isinstance(self.node, Node)
        assert isinstance(time, (int, long, float))
        assert time > 0


    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.node.name)

    def disruption_start(self):
        pass

    def disruption_end (self):
        pass

    def probe_status_change(self):
        if not self.is_disrupted:
            self.is_disrupted = True
            self.disruption_start()
        else:
            self.is_disrupted = False
            self.disruption_end()

    def run(self):
        while True:
            self.probe_status_change()
            yield self.env.timeout(self.time)


###################################################### Downtime


class Downtime(BaseDisruption):
    """
    temporarily deactivates the node
    """

    def __init__(self, env, node, time):
        super(Downtime, self).__init__(env, node, time)

    def disruption_start(self):
        self.node.active = False
        self.log("%.4f" % self.env.now + " " +str(self.node)+"\tis down")
        self.node.indicate(Node_Down())

    def restore_state(self):
        pass

    def disruption_end(self):
        self.node.active = True
        self.log("%.4f" % self.env.now + " " +str(self.node) + "\tis running")
        self.node.indicate(Node_Running())
        self.restore_state() # execute restore state operations or node boostrap if it is needed

###################################################### Crash Stop





class Crash_Stop (BaseDisruption):

    def __init__(self, env, node, time):
        super(Crash_Stop, self).__init__(env, node, time)
        assert isinstance(time, (int, long, float))
        assert time > 0
        self.time = time

    def disruption_start(self):
        self.node.indicate(Node_Down())
        if (self.node.active == True):
                self.node.active = False
                self.log("%.4f" % self.env.now + " " +str(self.node) + "\tis down")

    def disruption_end(self):
        pass

    def run(self):
        self.disruption_start()
        yield self.env.timeout(self.time)

"""
class Slowdown(BaseDisruption):

    temporarily reduces bandwidth

    availability = 0.7 # full bandwidth
    interval = 1.
    bandwitdh_reduction = 0.2

    def __init__(self, env, node, mtbf = 30):
        super(Slowdown, self).__init__(env, node)
        self.original_bandwidth = node.bandwidth_dl
        self.original_ul_bandwidth = node.bandwidth_ul
        self.mtbf = mtbf
    def disruption_start(self):
        self.node.bandwidth_ul *= self.bandwitdh_reduction
        self.node.bandwidth_dl *= self.bandwitdh_reduction

    def disruption_end(self):
        self.node.bandwidth_dl = self.original_dl_bandwidth
        self.node.bandwidth_ul = self.original_ul_bandwidth
"""