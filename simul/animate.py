import matplotlib.pyplot as plt
import networkx as nx # TODO: fix network visualization support
from matplotlib.animation import FuncAnimation


def avg_bandwidth(nodes):
    bws = []
    for node in nodes:
        for c in node.connections.values():
            bws.append(c.bandwidth)
    return sum(bws)/len(bws)

def median_bandwidth(nodes):
    bws = []
    for node in nodes:
        for c in node.connections.values():
            bws.append(c.bandwidth)
    bws.sort()
    return bws[len(bws)/2]

def max_nodes(nodes):
    return max(len(p.connections) for p in nodes)

def min_nodes(nodes):
    return min(len(p.connections) for p in nodes)


class Visualizer(object):

    def __init__(self, env, nodes, simulation_time):
        self.env = env
        self.nodes = nodes
        self.simulation_time = simulation_time
        fig = plt.figure(figsize=(8, 8))
        # interval: draws a new frame every *interval* milliseconds
        anim = FuncAnimation(fig, self.update, interval=50, blit=False)
        plt.show()

    def update_simulation(self):
        self.env.run(self.env.now + 1)

    def update(self, n):
#        print 'update simulation'
        # create graph
        G = nx.Graph()
        for node in self.nodes:
            G.add_node(node, label=node.name)
        for node in self.nodes:
            for other, cnx in node.connections.items():
                G.add_edge(node, other, weight=cnx.bandwidth)

        pos = nx.circular_layout(G)
        plt.cla()

        edges = nx.draw_networkx_edges(G, pos)
        nodes = nx.draw_networkx_nodes(G, pos, node_size=20)

        labels = dict((p, p.name) for p in self.nodes)
        nx.draw_networkx_nodes(G, pos, labels=labels, font_color='k')

        plt.axis('off')

        KBit = 1024 / 8

        plt.text(0.5, 1.1, "time: %.2f" % self.env.now,
             horizontalalignment='left',
             transform=plt.gca().transAxes)
        plt.text(0.5, 1.07, "avg bandwidth = %d KBit" % (avg_bandwidth(self.nodes)/KBit),
             horizontalalignment='left',
             transform=plt.gca().transAxes)
        plt.text(0.5, 1.04, "median bandwidth = %d KBit" % (median_bandwidth(self.nodes)/KBit),
             horizontalalignment='left',
             transform=plt.gca().transAxes)
        plt.text(0.5, 1.01, "min/max connections %d/%d" % (min_nodes(self.nodes), max_nodes(self.nodes)),
             horizontalalignment='left',
             transform=plt.gca().transAxes)

        nx.draw_networkx_labels(G, pos, labels)

        if (self.env.now<self.simulation_time):
            self.update_simulation()

        return nodes,
