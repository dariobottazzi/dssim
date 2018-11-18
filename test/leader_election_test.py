########################################################################################################################
##
## configuration of the scenario to simulate
##
########################################################################################################################

import random
import simpy
from simul.node import Node
from simul.communication_channel import Channel_Factory
from simul.disruptions import Downtime, Node_Down, Node_Running
from components.failure_detector import *
from components.leader_election import *
from peermanager import Test_service

NUM_PEERS = 3
SIM_DURATION = 40

def create_small_setting (env):
    print "create a small setting with very few nodes"
    peers = []
    factory = Channel_Factory("FIFO_Channel")
    factory.verbose = True

    for i in range(NUM_PEERS):

        p = Node('P%d' % i, env, factory)
        #p.services.append(Perfect_Failure_Detector(env, p, 2, 7))
        p.services.append(Eventually_Perfect_Failure_Detector(env, p, 2, 7))
        p.services.append(Monarch_Election(env, p))

        peers.append(p)

    for i in range(NUM_PEERS):
        for j in range(NUM_PEERS):
            if (i!=j):
                peers[i].connect(peers[j])

    peers[0].services.append(Downtime(env, peers[0], 10))

    return peers


######################

print " _   _"
print "((___))"
print "[ O o ]"
print " \   /"
print " ('_') I am setting the simulator up\n\n"

# create env
env = simpy.Environment()

#peers = create_peers(NUM_PEERS, env)
peers = create_small_setting(env)
print 'starting sim'
env.run(until=SIM_DURATION)


print " _   _"
print "((___))"
print "[ X x ]"
print " \   /"
print " ('_') I am done\n\n"

