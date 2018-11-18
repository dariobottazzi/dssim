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
from simul.disruptions import Crash_Stop
from components.failure_detector import *

from peermanager import Test_service

NUM_PEERS = 10
SIM_DURATION = 40



#########################################

def managed_peer(name, env, channel_factory):
    p = Node(name, env, channel_factory)
    #fd = Perfect_Failure_Detector(env, p, 2, 5)
    fd = Eventually_Perfect_Failure_Detector(env, p, 2, 5)
    #env.process(fd)
    p.services.append(fd)

    dt = Downtime(env, p, 10)
    p.services.append(dt)

    p.services.append(App_Failure_Detector())
    #p.services.append(Slowdown(env, p))
    #p.services.append(Crash_Stop(env, p, 10))

    return p


def create_peers(num, env):
    print "create nodes"
    peers = []
    factory = Channel_Factory("FIFO_Channel")
    factory.verbose = False

    for i in range(num):
        p = managed_peer('P%d' % i, env, factory)
        #env.process(p)
        peers.append(p)

    for i in range(num):
        for j in range(num):
            if (i!=j):
                peers[i].connect(peers[j])

    return peers

#########################################

def create_small_setting (env):
    print "create a small setting with very few nodes"
    peers = []
    factory = Channel_Factory("FIFO_Channel")
    factory.verbose = True
    num_nodi = 3

    for i in range(num_nodi):

        p = Node('P%d' % i, env, factory)
        p.services.append(Perfect_Failure_Detector(env, p, 2, 7))
        #p.services.append(Eventually_Perfect_Failure_Detector(env, p, 4, 8))
        p.services.append(App_Failure_Detector())

        peers.append(p)

    for i in range(num_nodi):
        for j in range(num_nodi):
            if (i!=j):
                peers[i].connect(peers[j])

    peers[2].services.append(Downtime(env, peers[2], 10))

    return peers


#####################



class App_Failure_Detector (BaseService):

    def handle_message(self, msg):
        if isinstance(msg, Availability_Internal_Message):
            print str(msg.data)




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

