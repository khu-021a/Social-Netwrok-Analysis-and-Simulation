
import networkx as nx 
import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics.ThresholdModel as th
from ndlib.viz.mpl.DiffusionTrend import DiffusionTrend

# Network topology

g = nx.gnm_random_graph(1000, 0.1)

# Model selection
model = th.ThresholdModel(g)

# Model Configuration
config = mc.Configuration()
config.add_model_parameter('percentage_infected', 0.1)

# Setting node parameters
threshold = 0.25
for i in g.nodes():
    config.add_node_configuration("threshold", i, threshold)

model.set_initial_status(config)

# Simulation execution
iterations = model.iteration_bunch(200)
trends = model.build_trends(iterations)

# Visualization
viz = DiffusionTrend(model, trends)
viz.plot("diffusion.pdf")