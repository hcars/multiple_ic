"""
This file defines a multiple IC model that follows the model as discussed
in the Carscadden_dm_work repository.
"""
import numpy as np
import snap
from typing import List


class multiple_IC:
    """
    Nodes spread each disease they are actively infected with for one time step before reverting to being recovered.

    A SNAP.py PNEANet is used as the disease graph.

    An array stating the names of the contagions is required. Note: This is restricted to two contagions for now.
    Counts of each disease are maintained.

    The nodes actively infected with each disease are stored in arrays.

    An indicator for the number of time steps is maintained for the simulations.

    An array indicating the names of the edge attributes for each disease must be provided in the same order as the
    names of the contagions.
    """

    def __init__(self, network: snap.PNEANet, contagion_names: List = ['Contagion 1', 'Contagion 2'],
                 edge_attribute_names: List = ['Contagion 1', 'Contagion 2']):
        self.network = network
        self.contagion_names = contagion_names
        self.edge_attribute_names = edge_attribute_names
        # Set metadata
        self.t = 0
        self.infected = []

    def set_seed_nodes(self, infected: dict):
        """
        Sets the seed nodes for the infection
        :param infected: A dict containing the infected node ids mapped to a list of the indices of the contagion name.
        :return: None
        """
        self.infected = list(infected.keys())
        for id in self.infected:
            for index in self.infected[id]:
                self.network.AddIntAttrDatN(id, infected[id], self.contagion_names[index])

    def iterate(self):
        """
        Completes one iteration of the IC model.
        :return: None
        """
        nodes_to_update = {}
        for node in self.infected:
            infected_status = []
            for contagion in self.contagion_names:
                infected_status.append(self.network.GetIntAttrDatN(node, contagion))
            for i in range(len(infected_status)):
                if infected_status[i] == 1:
                    node_iter = self.network.GetNI(node)
                    for id in node_iter.GetOutEdges():
                        edge_iter = self.network.GetEI(node_iter.GetId(), id)
                        edge_probability = self.network.GetFltAttrDatN(edge_iter, self.contagion_names[i])
                        trial = np.random.random()
                        if trial <= edge_probability and self.network.GetIntAttrDatN(id, self.contagion_names[i]) == 0:
                            try:
                                curr_update = nodes_to_update[id]
                                curr_update[i] = 1
                            except KeyError as key_e:
                                curr_update = [self.network.GetIntAttrDatN(id, self.contagion_names[j]) for j in
                                               range(len(self.contagion_names))]
                                curr_update[i] = 1
                                nodes_to_update[id] = curr_update
                    try:
                        curr_update = nodes_to_update[node]
                        curr_update[i] = 2
                    except KeyError as key_e:
                        curr_update = [self.network.GetIntAttrDatN(node, self.contagion_names[j]) for j in
                                       range(len(self.contagion_names))]
                        curr_update[i] = 2
                        nodes_to_update[node] = curr_update
        keys = list(nodes_to_update.keys())
        new_infected = []
        for i in range(len(keys)):
            node = keys[i]
            for j in range(len(self.contagion_names)):
                if nodes_to_update[node][j] == 1:
                    new_infected.append(node)
                self.network.AddIntAttrDatN(node, nodes_to_update[node][j], self.contagion_names[j])
        self.infected = new_infected


