# configuration of the scenario to simulate

import random
import simpy
from simul.peer import Peer
from simul.communication_channel import Channel_Factory
from simul.disruptions import Downtime
from simul.disruptions import Slowdown

from peermanager import ConnectionManager
from peermanager import PingHandler
from peermanager import PeerRequestHandler



NUM_PEERS = 50
SIM_DURATION = 5
KBit = 1024/8
MBit = 1024 * KBit
VISUALIZATION = False # TODO: fix network visualization support

def managed_peer(name, env, channel_factory):
    p = Peer(name, env, channel_factory)
    p.services.append(ConnectionManager(p))
    p.services.append(PeerRequestHandler())
    p.services.append(PingHandler())
    p.services.append(Downtime(env, p))
    p.services.append(Slowdown(env, p))
    return p


def create_peers(peerserver, num, channel_factory):
    peers = []
    for i in range(num):
        p = managed_peer('P%d' % i, env, channel_factory)
        # initial connect to peerserver
        connection_manager = p.services[0]
        connection_manager.connect_peer(peerserver)
        peers.append(p)
    # set DSL bandwidth
    for p in peers[:int(num * 0.5)]:
        p.bandwidth_ul = max(384, random.gauss(12000, 6000)) * KBit
        p.bandwidth_dl = max(128, random.gauss(4800, 2400)) * KBit
    # set hosted bandwidth
    for p in peers[int(num * 0.5):]:
        p.bandwidth_dl = p.bandwidth_ul = max(10000, random.gauss(100000, 50000)) * KBit
    return peers

# create env
env = simpy.Environment()

# bootstrapping peer
channel_factory = Channel_Factory("FIFO_Channel")
pserver = managed_peer('PeerServer', env, channel_factory)
pserver.bandwidth_ul = pserver.bandwidth_dl = 128 * KBit # super slow

# other peers
peers = create_peers(pserver, NUM_PEERS, channel_factory)

print 'starting sim'
if VISUALIZATION: # TODO: fix network visualization support
    from animate import Visualizer
    Visualizer(env, peers)
else:
    env.run(until=SIM_DURATION)

