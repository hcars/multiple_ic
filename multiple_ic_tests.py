import unittest

import snap

import multiple_ic


class MyTestCase(unittest.TestCase):
    network = snap.PNEANet.New()
    [network.AddNode(i) for i in range(6)]
    [network.AddIntAttrDatN(i, 0, 'Contagion ' + str(j)) for i in range(6) for j in range(1, 3)]
    edges = [(0, i) for i in range(1, 5)]
    for edge in edges:
        network.AddEdge(edge[0], edge[1])
        edge_id = network.GetEId(edge[0], edge[1])
        for i in range(1, 3):
            network.AddFltAttrDatE(edge_id, .1, 'Contagion ' + str(i))
    model = multiple_ic.multiple_IC(network)

    def test_set_seed(self):
        global model
        seed_set = {1: [1, 2]}
        model.set_seed_nodes(seed_set)


if __name__ == '__main__':
    unittest.main()
