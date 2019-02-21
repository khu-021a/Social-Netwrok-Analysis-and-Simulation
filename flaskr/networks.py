import random
import snap as sp

# four centralities
def degree_centrality(graph):
    return [sp.GetDegreeCentr(graph, node.GetId()) for node in graph.Nodes()]

def closeness_centrality(graph, normalized=True, is_directed=False):
    return [sp.GetClosenessCentr(graph, node.GetId(), normalized, is_directed) for node in graph.Nodes()]

def betweenness_centrality(graph, node_fraction=1.0, is_directed=False):
    nodes = sp.TIntFltH()
    edges = sp.TIntPrFltH()
    sp.GetBetweennessCentr(graph, nodes, edges, node_fraction, is_directed)
    return [nodes[n] for n in nodes], [edges[e] for e in edges]

def eigenvector_centrality(graph, eps=1e-4, max_iter=100):
    nodes = sp.TIntFltH()
    sp.GetEigenVectorCentr(graph, nodes, eps, max_iter)
    return [nodes[n] for n in nodes]

# three network generators
# rnd is a tuple including two integers (random seed and random step) for random numbers!!!
def net_rnd(nodes, edges, is_directed=False, is_multigraph=False, rnd=None):
    if rnd is None:
        rnd = sp.TRnd()
    else:
        rnd = sp.TRnd(*rnd)
    if is_directed:
        if is_multigraph:
            return sp.GenRndGnm(sp.PNEANet, nodes, edges, is_directed, rnd)
        else:
            return sp.GenRndGnm(sp.PNGraph, nodes, edges, is_directed, rnd)
    else:
        return sp.GenRndGnm(sp.PUNGraph, nodes, edges, is_directed, rnd)

def pref_attach(nodes, out_degree, rnd=None):
    if rnd is None:
        rnd = sp.TRnd()
    else:
        rnd = sp.TRnd(*rnd)
    return sp.GenPrefAttach(nodes, out_degree, rnd)

def small_world(nodes, out_degree, rewire_pb, rnd=None):
    if rnd is None:
        rnd = sp.TRnd()
    else:
        rnd = sp.TRnd(*rnd)
    return sp.GenSmallWorld(nodes, out_degree, rewire_pb, rnd)

# seed nodes generators
def rnd_seeds(node_num, seed_num):
    return random.sample(list(range(node_num)),seed_num)

def seeds(net, seed_num, indicator=None):
    methods = {
        'DC': degree_centrality,
        'BC': betweenness_centrality,
        'CC': closeness_centrality,
        'EC': eigenvector_centrality
    }

    def seeds_by_centrality(centralities, seed_num):
        sorted_indicators = sorted(list(enumerate(centralities)), key=lambda el: el[1], reverse=True)
        return  [indicator[0] for indicator in sorted_indicators[0: seed_num]]
    
    total_node_num = net.GetNodes()
    if seed_num >= total_node_num:
        return [node.GetId() for node in net.Nodes()]
    else:
        if indicator in methods:
            return seeds_by_centrality(methods[indicator](net), seed_num)
        else:
            return rnd_seeds(total_node_num, seed_num)

# community method
def community_cnm(graph):
    cc_vector = sp.TCnComV()
    sp.CommunityCNM(graph, cc_vector)
    return [list(nodes) for nodes in cc_vector]
    
# find sources in commutities
def find_transfer_sources(communities, proportion):
    index = [rnd_seeds(len(c), int(len(c) * proportion)) for c in communities]
    return [communities[i][n] for i in range(len(communities)) for n in index[i] if len(index[i]) > 0]

def find_opinion_leaders(graph, scale, ratio):
    if scale == "R":
        sources = find_transfer_sources(community_cnm(graph), ratio)
    else:
        sources = rnd_seeds(graph.GetNodes(), int(graph.GetNodes() * ratio))
    return sources

if __name__ == '__main__':
    #g = net_rnd(10, 10, rnd=(50, 10))
    #print {'nodes': [{'id': n.GetId()} for n in g.Nodes()], 'edges': [{'id': e[0], 'source': e[1].GetSrcNId(), 'target': e[1].GetDstNId()} for e in enumerate(g.Edges())]}
    c = [[0, 1, 2, 7], [3, 4, 5, 6, 8, 9]]
    print find_transfer_sources(c, 0.25)