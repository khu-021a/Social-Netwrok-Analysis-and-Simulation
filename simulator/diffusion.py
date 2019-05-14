import random
import snap as sp 


def LTM(net, seeds, threshold):
    if threshold > 1 or threshold < 0:
        threshold = random.uniform(0, 1)
    nbrs_nodes = set([])

    seeds_clone = [n for n in seeds]
    
    results = []
    results.append(seeds)
    
    for node in seeds_clone:
        seed_nbrs = set([v for v in net.GetNI(node).GetOutEdges() if v not in seeds_clone])
        nbrs_nodes = nbrs_nodes | seed_nbrs
    
    while len(nbrs_nodes) > 0:
        v = nbrs_nodes.pop()
        in_nbrs = [n for n in net.GetNI(v).GetInEdges()]
        in_active_nbrs = [n for n in net.GetNI(v).GetInEdges() if n in seeds_clone]
        buv = 1.0 * len(in_active_nbrs) / len(in_nbrs)
        if buv >= threshold:
            seeds_clone.append(v)
            results.append([v])
            new_nbrs = (n for n in net.GetNI(v).GetOutEdges() if n not in seeds_clone)
            nbrs_nodes = nbrs_nodes | set(new_nbrs)
    
    return results

def ICM(net, seeds, transfer_sources, pb_source, pb_normal):
    hist_seeds = set(seeds)
    
    results = []
    results.append(seeds)

    while len(seeds) > 0:
        seed_nbrs = set([v for node in seeds for v in net.GetNI(node).GetOutEdges() if v not in hist_seeds])
        pbnbrs = {n: random.uniform(0,1) for n in seed_nbrs}
        #new_seeds = set()
        new_seeds = []
        for k, v in pbnbrs.items():
            s = [n for n in net.GetNI(k).GetInEdges() if n in seeds]
            s_pb = [(pb_source if n in transfer_sources else pb_normal) for n in s]
            effective_pb = filter(lambda x : x >= v, s_pb)
            if len(effective_pb) > 0 and k not in hist_seeds:
                #new_seeds.add(k)
                new_seeds.append(k)
                results.append([k])
        hist_seeds = hist_seeds | set(new_seeds)
        seeds = new_seeds
    
    return results

'''
if __name__ == '__main__':
    import json
    import transform as t
    g = t.dict2graph(json.loads('{"nodes": [{"id": 0}, {"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}, {"id": 6}, {"id": 7}, {"id": 8}, {"id": 9}, {"id": 10}, {"id": 11}, {"id": 12}, {"id": 13}, {"id": 14}, {"id": 15}, {"id": 16}, {"id": 17}, {"id": 18}, {"id": 19}], "edges": [{"source": 0, "id": 0, "target": 2}, {"source": 0, "id": 1, "target": 4}, {"source": 0, "id": 2, "target": 6}, {"source": 0, "id": 3, "target": 8}, {"source": 0, "id": 4, "target": 13}, {"source": 0, "id": 5, "target": 18}, {"source": 0, "id": 6, "target": 19}, {"source": 1, "id": 7, "target": 2}, {"source": 1, "id": 8, "target": 3}, {"source": 1, "id": 9, "target": 6}, {"source": 1, "id": 10, "target": 7}, {"source": 1, "id": 11, "target": 10}, {"source": 1, "id": 12, "target": 11}, {"source": 1, "id": 13, "target": 12}, {"source": 1, "id": 14, "target": 14}, {"source": 1, "id": 15, "target": 15}, {"source": 1, "id": 16, "target": 16}, {"source": 1, "id": 17, "target": 18}, {"source": 2, "id": 18, "target": 3}, {"source": 2, "id": 19, "target": 5}, {"source": 2, "id": 20, "target": 6}, {"source": 2, "id": 21, "target": 11}, {"source": 2, "id": 22, "target": 15}, {"source": 2, "id": 23, "target": 16}, {"source": 2, "id": 24, "target": 17}, {"source": 3, "id": 25, "target": 7}, {"source": 3, "id": 26, "target": 8}, {"source": 3, "id": 27, "target": 12}, {"source": 3, "id": 28, "target": 16}, {"source": 3, "id": 29, "target": 18}, {"source": 4, "id": 30, "target": 8}, {"source": 4, "id": 31, "target": 10}, {"source": 4, "id": 32, "target": 11}, {"source": 4, "id": 33, "target": 12}, {"source": 4, "id": 34, "target": 13}, {"source": 4, "id": 35, "target": 14}, {"source": 4, "id": 36, "target": 18}, {"source": 5, "id": 37, "target": 7}, {"source": 5, "id": 38, "target": 12}, {"source": 5, "id": 39, "target": 14}, {"source": 5, "id": 40, "target": 17}, {"source": 6, "id": 41, "target": 7}, {"source": 6, "id": 42, "target": 8}, {"source": 6, "id": 43, "target": 12}, {"source": 6, "id": 44, "target": 13}, {"source": 6, "id": 45, "target": 14}, {"source": 6, "id": 46, "target": 17}, {"source": 6, "id": 47, "target": 18}, {"source": 7, "id": 48, "target": 8}, {"source": 7, "id": 49, "target": 10}, {"source": 7, "id": 50, "target": 12}, {"source": 7, "id": 51, "target": 13}, {"source": 7, "id": 52, "target": 15}, {"source": 7, "id": 53, "target": 18}, {"source": 8, "id": 54, "target": 9}, {"source": 8, "id": 55, "target": 11}, {"source": 8, "id": 56, "target": 12}, {"source": 8, "id": 57, "target": 13}, {"source": 8, "id": 58, "target": 14}, {"source": 8, "id": 59, "target": 15}, {"source": 9, "id": 60, "target": 12}, {"source": 9, "id": 61, "target": 13}, {"source": 9, "id": 62, "target": 14}, {"source": 9, "id": 63, "target": 15}, {"source": 10, "id": 64, "target": 11}, {"source": 10, "id": 65, "target": 12}, {"source": 10, "id": 66, "target": 13}, {"source": 10, "id": 67, "target": 14}, {"source": 10, "id": 68, "target": 16}, {"source": 10, "id": 69, "target": 18}, {"source": 11, "id": 70, "target": 14}, {"source": 11, "id": 71, "target": 18}, {"source": 12, "id": 72, "target": 16}, {"source": 12, "id": 73, "target": 17}, {"source": 13, "id": 74, "target": 16}, {"source": 13, "id": 75, "target": 18}, {"source": 13, "id": 76, "target": 19}, {"source": 14, "id": 77, "target": 17}, {"source": 14, "id": 78, "target": 18}, {"source": 15, "id": 79, "target": 19}]}'))
    seeds = [14, 19, 11]
    op_l = [13, 16, 6]
    pb_op = 0.3
    pb_norm = 0.2
    print ICM(g, seeds, op_l, pb_op, pb_norm)
'''
