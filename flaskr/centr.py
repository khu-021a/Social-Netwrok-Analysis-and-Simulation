import snap as sp 
import graph

def centr(graph):
    return [sp.GetDegreeCentr(graph, node.GetId()) for node in graph.Nodes()]

def closeness(graph, normalized = True, IsDir = False):
    return [sp.GetClosenessCentr(graph, node.GetId()) for node in graph.Nodes()]

def between(graph, nodeFrac = 1.0, IsDir = False):
    nodes = sp.TIntFltH()
    edges = sp.TIntPrFltH()
    sp.GetBetweennessCentr(graph, nodes, edges, nodeFrac, IsDir)
    # return nodes and edges, user needs nodes.
    return [nodes[n] for n in nodes], [edges[e] for e in edges]

def eigenvector(graph, Eps = 1e-4, MaxIter = 100):
    nodes = sp.TIntFltH()
    sp.GetEigenVectorCentr(graph, nodes,  Eps, MaxIter)
    # return nodes and edges, user needs nodes.
    return [nodes[n] for n in nodes]

"""g1= graph.prefattach_gnm( 5,2)
xxx=eigenvector(g1)
# print([node.GetId() for node in g1.Nodes()])
print(xxx)"""
