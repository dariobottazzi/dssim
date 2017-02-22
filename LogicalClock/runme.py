########################################################################################################################
##
## configuration of the scenario to simulate
##
########################################################################################################################

import random
import simpy
from simul.peer import Peer
from simul.disruptions import Downtime
from simul.disruptions import Slowdown

from  peermanager import Lamport_clock_service

NUM_PEERS = 5
SIM_DURATION = 50
KBit = 1024/8
MBit = 1024 * KBit


#########################################

def managed_peer(name, env):
    p = Peer(name, env)
    p.services.append(Lamport_clock_service(env, p))
    p.services.append(Downtime(env, p))
    p.services.append(Slowdown(env, p))
    return p

#########################################


def create_peers(num, env):
    peers = []
    for i in range(num):
        p = managed_peer('P%d' % i, env)
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
env.run(until=SIM_DURATION)

print "------------------- Situation after the end of the execution"
for i in peers:
    print i, i.services[0].clock
print "------------------------------------------------------------"