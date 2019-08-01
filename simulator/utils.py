import numpy as np

def flatten_list_2d(list_2d):
    return reduce(lambda x, y: x + y, list_2d, [])

def node_centrality_equal_intervals(centralities):
    num_nodes = len(centralities)
    num_intv = 4
    max_val = max(centralities)
    min_val = min(centralities)
    def generate_equal_intervals(num, min_val, max_val):
        if num <= 1:
            return [(min_val, max_val)]
        else:
            diff = max_val - min_val
            step = diff / num
            lower_bounds = [min_val + step * n for n in range(num)]
            upper_bounds = [min_val + step * n for n in range(1, num + 1)]
            return zip(lower_bounds, upper_bounds)
    bounds = generate_equal_intervals(num_intv, min_val, max_val)
    bound_pairs = [list(b) for b in bounds]
    bound_pairs[-1][-1] += 1 
    counters = [len(filter(lambda n: p[0] <= n < p[1], centralities)) for p in bound_pairs]
    c_array = np.asarray(centralities)
    classes = reduce(lambda x, y: x + y, [np.where(np.logical_and(p[0] <= c_array, c_array < p[1]), i + 1, 0) for i, p in enumerate(bound_pairs)]).tolist()
    return classes, [{'lower': k[0][0], 'upper': k[0][1], 'number': k[1], 'ratio': k[1] * 1.0 / num_nodes} for k in zip(bounds, counters)]

def preprocess_cl_results(results):
    init = list(results[0:1])
    rest = list(results[1:])
    flat_rest = reduce(lambda x, y: x + y, rest)
    return init + [[el] for el in flat_rest]

def list2d2dict(list2d):
    tmp = [[(el, t[0]) for el in t[1]] for t in enumerate(list2d)]
    d = dict([el for l in tmp for el in l])
    return d

def get_acc_list(input_list):
    new_list = []
    length = len(input_list)
    while 0 < length:
        new_list.insert(0, sum(input_list[0:length]))
        length -= 1
    return new_list

def merge_results(net, seeds=None, opinion_leaders=None, communities=None, diffused=None):
    nodes = net['nodes']
    new_nodes = []
    for n in nodes:
        n_id = n['id']
        if seeds is not None:
            n['seed'] = (n_id in seeds)
        if opinion_leaders is not None:
            n['leader'] = (n_id in opinion_leaders)
        if communities is not None:
            c = list2d2dict(communities)
            n['community'] = c[n_id] if n_id in c else -1
        if diffused is not None:
            d = list2d2dict(diffused)
            n['diffused'] = d[n_id] if n_id in d else -1
        new_nodes.append(n)
    return {'nodes': new_nodes, 'edges': net['edges']}