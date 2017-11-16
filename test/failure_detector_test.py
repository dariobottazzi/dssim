########################################################################################################################
##
## configuration of the scenario to simulate
##
########################################################################################################################

import random
import simpy
from simul.node import Node
from simul.communication_channel import Channel_Factory
from simul.disruptions import Downtime
from simul.disruptions import Crash_Stop
from components.failure_detector import *

from peermanager import Test_service

NUM_PEERS = 100
SIM_DURATION = 100


#########################################

def managed_peer(name, env, channel_factory):
    p = Node(name, env, channel_factory)
    p.services.append(Perfect_Failure_Detector(env, p, 10))
    p.services.append(App_Failure_Detector())
    #p.services.append(Downtime(env, p, 10))
    #p.services.append(Slowdown(env, p))
    #p.services.append(Crash_Stop(env, p, 10))
    return p

#########################################


def create_peers(num, env):
    print "create nodes"
    peers = []
    factory = Channel_Factory("FIFO_Channel")
    for i in range(num):
        p = managed_peer('P%d' % i, env, factory)
        peers.append(p)

    for i in range(num):
        for j in range(num):
            if (i!=j):
                peers[i].connect(peers[j])


    return peers

######################

print " _   _"
print "((___))"
print "[ O o ]"
print " \   /"
print " ('_') I am setting the simulator up\n\n"

# create env
env = simpy.Environment()

peers = create_peers(NUM_PEERS, env)

print 'starting sim'
env.run(until=SIM_DURATION)
