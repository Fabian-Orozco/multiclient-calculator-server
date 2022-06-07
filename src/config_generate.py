# 200 OK: Random network configuration file generator.
# Taken from: https://stackoverflow.com/a/61961881

# hacer local y cuidar puertos

import sys
import networkx as nx
import random
import matplotlib.pyplot as plt
from itertools import combinations, groupby

# Redirect output to csv file:
# python3 config_generate.py nodes > config.csv

# Generates a random weighted connected graph according to number of nodes n and probability
# of two nodes being connected p. Then completes the graph if any node is not yet connected.
def random_connected_graph(n, p):
    edges = combinations(range(n), 2)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    if p <= 0:
        return G
    if p >= 1:
        return nx.complete_graph(n, create_using=G)
    for _, node_edges in groupby(edges, key=lambda x: x[0]):
        node_edges = list(node_edges)
        random_edge = random.choice(node_edges)
        G.add_edge(*random_edge, weight = random.randint(1,5))
        for e in node_edges:
            if random.random() < p:
                G.add_edge(*e, weight = random.randint(1,5))
    return G

# Main program that generates the random graph and outputs the formatted configuration.
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please specify the number of nodes the generated graph will have.")
        exit()
    
    seed = random.randint(1,10)
    
    # All available IPs:
    ips = ["172.16.202.167", "172.16.202.169", "172.16.202.180", "172.16.202.185", "172.16.202.191","172.16.202.192","172.16.202.44"]
    random.shuffle(ips)

    # Number of nodes to create based on input parameter:
    nodes = int(sys.argv[1])

    # Probability of two nodes being connected:
    probability = 0.1
    G = random_connected_graph(nodes, probability)

    # Print a formatted line for every edge in the graph:
    edges = list(G.edges(data = True))
    port = 50000
    conn = "{A},{IP_A},{Port_A},{B},{IP_B},{Port_B},{W}"
    for node in edges:
        print(conn.format(A = chr(node[0]+65), IP_A = ips[node[0] % len(ips)], Port_A = port, \
            B = chr(node[1]+65), IP_B = ips[node[1] % len(ips)], Port_B=(port+10), W = node[2]['weight']), end="")
        if node != edges[-1]:
            print()
        port = port + 20
    
    """ pos = nx.spring_layout(G, seed=7)
    nx.draw_networkx_nodes(G, pos, node_size=500)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels)
    plt.show() """
