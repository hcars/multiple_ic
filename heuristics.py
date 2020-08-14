import random
from queue import Queue

import networkx as nx

sorted_by_degree = lambda G: sorted(list(nx.degree_centrality(G).items()), reverse=True, key=lambda x: x[1])


def degree_heuristic(G, k, infectivity_1, infectivity_2):
    """
    This takes a graph, a requested number of seed nodes, the infectivity of two contagions, and provides a seed set.
    :param G: The input epidemic graph.
    :param k: The required number of seed nodes.
    :param infectivity_1: The infection probability for contagion 1.
    :param infectivity_2: The infection probability for contagion 2.
    :return: A seed set.
    """
    degree_distribution = sorted_by_degree(G)
    seed_set = []
    ptr = 0
    while len(seed_set) < k:
        new_seed = degree_distribution[ptr][0]
        if infectivity_1 == infectivity_2:
            if random.random() <= .5:
                best = 0
            else:
                best = 1
        elif infectivity_1 < infectivity_2:
            best = 1
        else:
            best = 0
        seed_set.append((new_seed, best))
        ptr += 1
    return seed_set


def random_control(G, k):
    """
    This takes a graph and required number of seed nodes and then returns a seed set chosen uniformly randomly from the
    graph. Contagions are assigned to seed nodes uniformly randomly.
    :param G: The input epidemic graph.
    :param k: The number of seed nodes required.
    :return: The seed set for the simulation.
    """
    nodes = list(G.nodes(data=False))
    seed_set = []
    while len(seed_set) < k:
        node_index = random.randrange(0, len(nodes))
        if nodes[node_index] not in seed_set:
            if random.random() <= .5:
                seed_set.append((nodes[node_index], 0))
            else:
                seed_set.append((nodes[node_index], 1))
    return seed_set


def random_cascade(G, seed_set, infectivity_1, infectivity_2, additive_interaction_1=.1,
                   additive_interaction_2=.1):
    cascade_queue = Queue()
    infected_total = len(seed_set)
    for seed_node in seed_set:
        cascade_queue.put(seed_node[0])
    while not cascade_queue.empty():
        node = cascade_queue.get()
        for i in range(2):
            for neighbors in nx.neighbors(G, node):
                node_state = G.nodes[node][str(i)]
                if not G.nodes[neighbors][str(i)] and node_state:
                    flip = random.random()
                    infectivity = 0
                    if i == 0:
                        infectivity = infectivity_1
                        if G.nodes[neighbors]['1']:
                            infectivity += additive_interaction_2
                    elif i == 1:
                        infectivity = infectivity_2
                        if G.nodes[neighbors]['0']:
                            infectivity += additive_interaction_1
                    if flip <= infectivity:
                        G.nodes[neighbors][str(i)] = True
                        cascade_queue.put(neighbors)
                        infected_total += 1
    return infected_total


def KKT(G, k, seed_set, iterations, infectivity_1, infectivity_2, additive_interaction_1=.1,
        additive_interaction_2=.1):
    seed_set = []
    while len(seed_set) < k:
        infected_max = 0
        node_max = 0
        nodes = list(G.nodes)
        for node in nodes:
            infected = 0
            for i in range(iterations):
                infected += random_cascade(G, seed_set, infectivity_1, infectivity_2, additive_interaction_1,
                                           additive_interaction_2)
            infected_avg = infected / iterations
            if infected_avg > infected_max:
                infected_max = infected_avg
                node_max = node
        if infectivity_1 == infectivity_2:
            if random.random() <= .5:
                best = 0
        elif infectivity_1 < infectivity_2:
            best = 1
        else:
            best = 0
        seed_set.append((node_max, best))
    return seed_set
