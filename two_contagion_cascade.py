import ndlib.models.CompositeModel as gc
import ndlib.models.ModelConfig as mc
import networkx as nx
from ndlib.models.compartments import NodeStochastic
import heuristics
import random

random.seed(a=27609)
G = nx.barabasi_albert_graph(2000, 3, seed=27609)

# Composite Model instantiation
model = gc.CompositeModel(G)

# Model statuses
model.add_status("Susceptible")
model.add_status("Infected")
model.add_status("Infected_2")
model.add_status("Infected_Both")
model.add_status("Removed")
# Compartment definition

contagion_1 = NodeStochastic(0.1, triggering_status="Infected")
contagion_2 = NodeStochastic(0.1, triggering_status="Infected_2")
contagion_both = NodeStochastic(0.1, triggering_status="Infected_Both")
contagion_interaction_1 = NodeStochastic(.2, triggering_status="Infected")
contagion_interaction_2 = NodeStochastic(1, triggering_status="Infected_2")
# Should be adjusted based on rate that KKT assumes in original paper.
recovered = NodeStochastic(1)


# Rule definition
model.add_rule("Susceptible", "Infected", contagion_1)
model.add_rule("Susceptible", "Infected_2", contagion_2)
model.add_rule("Susceptible", "Infected", contagion_both)
model.add_rule("Susceptible", "Infected_2", contagion_both)
model.add_rule('Infected', 'Infected_2', contagion_interaction_2)
model.add_rule('Infected_2', 'Infected', contagion_interaction_1)
for infected_state in ['Infected', 'Infected_2', 'Infected_Both']:
    model.add_rule(infected_state, 'Removed', recovered)

config = mc.Configuration()

seed_set = heuristics.degree_heuristic(G, 20, .1, .1)
# seed_set = heuristics.random_control(G, 10)
seed_set_1 = []
seed_set_2 = []
for i in range(len(seed_set)):
    if seed_set[i][1] == 0:
        seed_set_1.append(seed_set[i][0])
    else:
        seed_set_2.append(seed_set[i][0])
# seed_set_1 = [1, 1000, 2323, 311, 24324]
# # seed_set_2 = [2, 4123, 421]
#
config.add_model_initial_configuration('Infected', seed_set_1)
config.add_model_initial_configuration('Infected_2', seed_set_2)

model.set_initial_status(config)
# Simulation

iterations = model.iteration_bunch(100)
trends = model.build_trends(iterations)
# print(trends)
# for i in range(50):
#     for j in range(4):
#         print(trends[0]['trends']['node_count'][j][i])
#     print('---------------')

from bokeh.io import show
from ndlib.viz.bokeh.DiffusionTrend import DiffusionTrend

viz = DiffusionTrend(model, trends)
p = viz.plot(width=400, height=400)
show(p)

