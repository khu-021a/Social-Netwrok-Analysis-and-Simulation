import random
#import seeds
import snap as sp 
import graph

    
#threshold is the weight of each edge in the graph, user can define it. 
def linear(net, seednodes, threshold):
    if threshold > 1 or threshold < 0:
        threshold = random.uniform(0,1)
    
    
    nbrs_nodes = set([])
    #buv = {}
    
    for node in seednodes:
        seednbrs_nodes = set([v for v in net.GetNI(node).GetOutEdges() if v not in seednodes] )
        nbrs_nodes = nbrs_nodes | seednbrs_nodes 
    print(seednodes)
    while len(nbrs_nodes) > 0:
        v = nbrs_nodes.pop()
        in_nbrs = [n for n in net.GetNI(v).GetInEdges()]
        in_active_nbrs = [n for n in net.GetNI(v).GetInEdges() if n in seednodes]
        buv = 1.0 * len(in_active_nbrs) / len(in_nbrs)
        if buv >= threshold:
            seednodes.append(v)
            new_nbrs = (n for n in net.GetNI(v).GetOutEdges() if n not in seednodes)
            nbrs_nodes = nbrs_nodes | set(new_nbrs)
        print(seednodes)
        print(nbrs_nodes)


    """while True:
        toact_nodes = set ([v for x in seednodes for v in net.GetNI(x).GetOutEdges() if v not in seednodes])
        nbrs_nodes = nbrs_nodes | toact_nodes 
        print(nbrs_nodes)
        for toact_node in list(nbrs_nodes):
            toact_edges = set ([v for v in net.GetNI(toact_node).GetInEdges() if v in seednodes])
            pb_edge = 1/float(len(toact_edges))
            pb_edges = 0
            for edge in toact_edges:
                pb_edges = pb_edges+pb_edge
            if pb_edges >= threshold:
                seednodes.append(toact_node)
                nbrs_nodes.remove(toact_node)
        if not nbrs_nodes:
            print(seednodes)
            break"""

        
    
g1= graph.rnd_gnm(sp.PUNGraph,5,2)
    #seednodes=[1,3]
linear(g1, [1,2], 0.4 )
           
        #pbnode = random.uniform(0,1)
       
        
     
        

    
    