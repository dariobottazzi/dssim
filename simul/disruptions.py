
from services import BaseService

class BaseDisruption(BaseService):   # TODO: controllare le disruption e verificare che le cose vadano come atteso
    """
    the class changes on-line behaviour of the node at regular times
    """
    is_disrupted = False

    def __init__(self, env, node, time):
        self.env = env
        self.node = node
        self.env.process(self.run())
        self.time = time # secs (time between failures)

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


class Downtime(BaseDisruption):
    """
    temporarily deactivates the node
    """

    def __init__(self, env, node, time):
        super(Downtime, self).__init__(env, node, time)

    def disruption_start(self):
        self.node.active = False
        print "node", self.node, "is down"

    def restore_state(self):
        pass

    def disruption_end(self):
        self.node.active = True
        print "node", self.node, "is up again"
        self.restore_state() # execute restore state operations or node boostrap if it is needed



class Crash_Stop (BaseDisruption):

    def __init__(self, env, node, time):
        super(Crash_Stop, self).__init__(env, node, time)
        self.time = time

    def disruption_start(self):
        if (self.node.active == True):
                self.node.active = False
                print "node", self.node, "is down"

    def disruption_end(self):
        pass

    def run(self):
        yield self.env.timeout(self.time)
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