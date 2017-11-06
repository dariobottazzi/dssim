import random

from node import BaseService

class BaseDisruption(BaseService):   # TODO: controllare le disruption e verificare che le cose vadano come atteso
    availability = 0.97
    interval = 1.
    is_disrupted = False

    def __init__(self, env, node, mtbf = 100):
        self.env = env
        self.node = node
        self.env.process(self.run())
        self.mtbf = mtbf # secs (mean time between failures)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.node.name)

    def disruption_start(self):
        pass

    def disruption_end (self):
        pass

    def probe_status_change(self):
        if not self.is_disrupted:
            if random.random() < self.interval / self.mtbf:
                self.is_disrupted = True
                self.disruption_start()
        else:
            avg_disruption_duration = self.mtbf * (1 - self.availability)
            if random.random() < self.interval / avg_disruption_duration:
                self.is_disrupted = False
                self.disruption_end()

    def run(self):
        while True:
            self.probe_status_change()
            yield self.env.timeout(self.interval)


class Downtime(BaseDisruption):
    """
    temporarily deactivates the node
    """

    availability = 0.4
    interval = 1.

    def __init__(self, env, node, mtbf = 100):
        super(Downtime, self).__init__(env, node, mtbf)

    def disruption_start(self):
        self.node.active = False

    def restore_state(self):
        pass

    def disruption_end(self):
        self.node.active = True
        self.restore_state() # execute restore state operations or node boostrap if it is needed



class Crash_Stop (BaseDisruption):

    def __init__(self, env, node, mtbf = 100, interval = 5):
        super(Crash_Stop, self).__init__(env, node, mtbf)
        self.interval = interval

    def disruption_start(self):
        if (self.node.active == True):
                self.node.active = False
                print "node", self.node, "is down"


    def disruption_end(self):
        pass


    def run(self):
        yield self.env.timeout(self.interval)
        self.disruption_start()

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