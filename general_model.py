import future.utils
import networkx as nx
import numpy as np
from ndlib.models.DiffusionModel import DiffusionModel
from netdispatch import AGraph

G = nx.Graph()

# p_1 is the infection probability for contagion 1
p_1 = .1
# p_2 is the infection probability for contagion 2
p_2 = .1
# The infection probabilities for transitioning to both from infected states.
p_both_given_c1 = .1
p_both_given_c2 = .1


class multiple_independent_cascade(DiffusionModel):

    def __init__(self, graph, seed=None):
        """
                    Model Constructor
                    :param graph: A networkx graph object
                """

        np.random.seed(seed)

        self.discrete_state = True

        self.params = {
            'nodes': {},
            'edges': {
                "threshold_1": {
                    "descr": "Infection rate for contagion 1.",
                    "range": [0, 1],
                    "optional": False},
                "threshold_2": {
                    "descr": "Infection rate for contagion 2.",
                    "range": [0, 1],
                    "optional": False},
                "infection_1_given_2": {
                    "descr": "Infection rate for contagion 1 given infected with contagion 2.",
                    "range": [0, 1],
                    "optional": False
                },
                "infection_2_given_1": {
                    "descr": "Infection rate for contagion 2 given infected with contagion 1.",
                    "range": [0, 1],
                    "optional": False
                },
            },
            'model': {},
            'status': {}
        }
        self.available_statuses = {}
        cnt = 0
        for i in range(3):
            for j in range(3):
                self.available_statuses[(i, j)] = cnt
                cnt += 1
        self.name = "multiple_IC"

        self.actual_iteration = 0
        self.graph = AGraph(graph)
        self.status = {n: 0 for n in self.graph.nodes}
        self.initial_status = {}

    def iteration(self, node_status=True):
        """
        Execute a single model iteration
        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        self.clean_initial_status(self.available_statuses.values())
        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(actual_status)
            if node_status:
                return {"iteration": 0, "status": actual_status.copy(),
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
            else:
                return {"iteration": 0, "status": {},
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}

        for u in self.graph.nodes:
            for i in range(2):
                if self.status[u][i] != 1:
                    continue

                neighbors = list(
                    self.graph.neighbors(u))  # neighbors and successors (in DiGraph) produce the same result

                # Standard threshold
                if len(neighbors) > 0:
                    threshold = 1.0 / len(neighbors)

                    for v in neighbors:
                        if actual_status[v][i] == 0:
                            key = (u, v)

                            if self.params['nodes']['com'][u] == self.params['nodes']['com'][
                                v]:  # within same community
                                # Individual specified thresholds
                                if 'threshold_' + str(i) in self.params['edges']:
                                    if key in self.params['edges']['threshold_' + str(i)]:
                                        threshold = self.params['edges']['threshold_' + str(i)][key]
                                    elif (v, u) in self.params['edges'][
                                        'threshold_' + str(i)] and not self.graph.directed:
                                        threshold = self.params['edges']['threshold_' + str(i)][(v, u)]

                            else:  # across communities
                                p = self.params['model']['permeability']
                                if 'threshold_' + str(i) in self.params['edges']:
                                    if key in self.params['edges']['threshold_' + str(i)]:
                                        threshold = self.params['edges']['threshold_' + str(i)][key] * p
                                    elif (v, u) in self.params['edges'][
                                        'threshold_' + str(i)] and not self.graph.directed:
                                        threshold = self.params['edges']['threshold_' + str(i)][(v, u)] * p

                            flip = np.random.random_sample()
                            if flip <= threshold:
                                actual_status[v][i] = 1

                actual_status[u][i] = 2

            delta, node_count, status_delta = self.status_delta(actual_status)
            self.status = actual_status
            self.actual_iteration += 1

            if node_status:
                return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
            else:
                return {"iteration": self.actual_iteration - 1, "status": {},
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
