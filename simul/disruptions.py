import random

from peer import BaseService


class BaseDisruption(BaseService):
    mtbf = 24. * 60 * 60 # secs (mean time between failures)
    availability = 0.97
    interval = 1.
    is_disrupted = False

    def __init__(self, env, peer):
        self.env = env
        self.peer = peer
        self.env.process(self.run())

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.peer.name)

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
    temporarily deactivates the peer
    """
    mtbf = 4. * 60  # secs (mean time between failures)
    availability = 0.4
    interval = 1.

    def __init__(self, env, peer):
        super(Downtime, self).__init__(env, peer)

    def disruption_start(self):
        self.peer.active = False

    def disruption_end(self):
        self.peer.active = True


class Crash_Stop (BaseDisruption):
    interval = 5.

    def __init__(self, env, peer):
        super(Crash_Stop, self).__init__(env, peer)

    def disruption_start(self):
        if (self.peer.active == True):
                self.peer.active = False
                print "peer", self.peer, "is down"


    def disruption_end(self):
        pass


    def run(self):
        #while True:
        yield self.env.timeout(self.interval)
        self.disruption_start()


class Slowdown(BaseDisruption):
    """
    temporarily reduces bandwidth
    """
    mtbf = 15 * 6 # secs (mean time between failures)
    availability = 0.7 # full bandwidth
    interval = 1.
    bandwitdh_reduction = 0.2

    def __init__(self, env, peer):
        self.original_dl_bandwidth = peer.bandwidth_dl
        self.original_ul_bandwidth = peer.bandwidth_ul
        super(Slowdown, self).__init__(env, peer)

    def disruption_start(self):
        self.peer.bandwidth_ul *= self.bandwitdh_reduction
        self.peer.bandwidth_dl *= self.bandwitdh_reduction

    def disruption_end(self):
        self.peer.bandwidth_dl = self.original_dl_bandwidth
        self.peer.bandwidth_ul = self.original_ul_bandwidth
