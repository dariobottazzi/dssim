########################################################################################################################
##
## configuration of the scenario to simulate
##
########################################################################################################################

import random
import simpy
from simul.peer import Peer
from simul.peer import Channel_Factory
from simul.disruptions import Downtime
from simul.disruptions import Slowdown
from simul.disruptions import Crash_Stop

from simul.animate import Visualizer

from  peermanager import Test_service

NUM_PEERS = 2
SIM_DURATION = 50
KBit = 1024/8
MBit = 1024 * KBit

VISUALIZATION = False

#########################################

def managed_peer(name, env, channel_factory):
    p = Peer(name, env, channel_factory)
    p.services.append(Test_service(env, p))
    p.services.append(Downtime(env, p))
    p.services.append(Slowdown(env, p))
    #p.services.append(Crash_Stop(env, p))
    return p

#########################################


def create_peers(num, env):
    peers = []
    factory = Channel_Factory("FIFO_Channel")
    for i in range(num):
        p = managed_peer('P%d' % i, env, factory)
        p.bandwidth_ul = max(384, random.gauss(12000, 6000)) * KBit
        p.bandwidth_dl = max(128, random.gauss(4800, 2400)) * KBit
        peers.append(p)

    for i in range(num):
        for j in range(num):
            if (i!=j):
                peers[i].connect(peers[j])

    return peers

# create env
env = simpy.Environment()

peers = create_peers(NUM_PEERS, env)
print 'starting sim'

if VISUALIZATION: # TODO: fix network visualization support
    Visualizer(env, peers, SIM_DURATION)
else:
    env.run(until=SIM_DURATION)

