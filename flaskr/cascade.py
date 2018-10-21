import random
import seeds
import snap as sp 
import graph
import community
    
#threshold is the weight of each edge in the graph, user can define it. 
def cascade(net, seednodes, pbopinion, pbnormal, opinleader, pbopinleader):
    if opinleader == "Each Network":
        olnodes = community.find_opinionleaders(community.communityCNM(net),pbopinleader)
    else:
        olnodes = seeds.rnd(net.GetNodes(),int(net.GetNodes()*pbopinleader))

    
    
    nbrs_nodes = set([])
    #buv = {}
    
    '''for node in seednodes:
        #seednbrs_nodes = set([v for v in net.GetNI(node).GetOutEdges() if v not in seednodes] )
        nbrs_nodes = nbrs_nodes | seednbrs_nodes 
    '''
    hist_seeds = set(seednodes)
    print(seednodes)
    while len(seednodes) > 0:
        seednbrs_nodes = set([v for node in seednodes for v in net.GetNI(node).GetOutEdges() if v not in hist_seeds] )
        print(seednbrs_nodes)
        pbnbrs = {n: random.uniform(0,1) for n in seednbrs_nodes}
        new_seeds = set()
        for k, v in pbnbrs.items():
            s = [n for n in net.GetNI(k).GetInEdges() if n in seednodes]
            s_pb = [(pbopinion if n in olnodes else pbnormal) for n in s]
            effective_pb = filter(lambda x : x >= v, s_pb)
            if len(effective_pb) > 0 and k not in hist_seeds:
                new_seeds.add(k)
        hist_seeds = hist_seeds | new_seeds
        seednodes = list(new_seeds)
        print(seednodes)
    print(hist_seeds)
    return hist_seeds




        
if __name__ == '__main__':
    g1= graph.rnd_gnm(sp.PUNGraph,20,60)
    print(cascade(g1, [1,12,5,9], 0.4, 0.3, "Each Network", 0.2 ))

       