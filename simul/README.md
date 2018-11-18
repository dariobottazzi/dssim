A simple simulation framework for distributed system. The main aim of this simulator is to simplify the design, development and testing of distributed algorithms.

The system is built on top othe the [simpy](https://simpy.readthedocs.org/en/latest/) event-based simulation framework and evolves from the [p2p network simulator](https://github.com/heikoheiko/p2p-network-simulator/).


Features
======================
Simulation of
- connections with bandwidth & latency
- messaging
- bootstrapping
- peer reorganisation based on bandwith & availability
- peer downtimes / disconnects
- network slowdowns

Usage
======================
To start the default simulation type ```python run.py```.

Browse and modify the source to model your problem.

The ```Peer``` class offers to register *services* which are based on the ```BaseService``` class. All registered services are called whenever a ```Message``` is received. Services as well as Peers are simpy-processes.