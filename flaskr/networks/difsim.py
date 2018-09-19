#! python3
import networkx as nx 
import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics.ThresholdModel as th
#from ndlib.viz.mpl.DiffusionTrend import DiffusionTrend
#from ndlib.viz.mpl.DiffusionPrevalence import DiffusionPrevalence

"""
# Network topology

g = nx.gnm_random_graph(200, 1000)

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
iterations = model.iteration_bunch(10)
trends = model.build_trends(iterations)

"""

# Visualization
"""
viz = DiffusionTrend(model, trends)
viz.plot('diffusion.pdf')
viz = DiffusionPrevalence(model, trends)
viz.plot("prevalence.pdf")"""



def difsim(n, m, modelpara, nodethre, ite):
    
    g = nx.gnm_random_graph(n, m)
    model = th.ThresholdModel(g)
    config = mc.Configuration()
    config.add_model_parameter('percentage_infected', modelpara)
    
    if isinstance(nodethre,dict):
        config.add_node_set_configuration("threshold", nodethre)
    elif isinstance(nodethre,(int,float)):
        if 0<nodethre<1:

            for i in g.nodes():
                config.add_node_configuration("threshold", i, nodethre)
        else: 
            raise ValueError()
    else:
        raise TypeError()

    model.set_initial_status(config)
    # Simulation execution
    data=[]
    difsimdata = model.iteration_bunch(ite)
    for i in difsimdata:
        ite = i['iteration']
        sus = i['node_count'][0]
        inf = i['node_count'][1]
        
        data.append({'iteration':ite, 'sus':sus, 'inf':inf})
    return data

   

