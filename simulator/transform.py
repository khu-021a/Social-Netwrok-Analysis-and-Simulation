import snap


def graph2dict(g):
    return {'nodes': [{'id': n.GetId()} for n in g.Nodes()], 'edges': [{'id': e[0], 'source': e[1].GetSrcNId(), 'target': e[1].GetDstNId()} for e in enumerate(g.Edges())]}

def dict2graph(d):
    nodes = d['nodes']
    edges = d['edges']
    g = snap.TUNGraph.New()
    for node in nodes:
        g.AddNode(int(node['id']))
    for edge in edges:
        g.AddEdge(int(edge['source']), int(edge['target']))
    return g