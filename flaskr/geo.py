import json
import numpy as np
import snap as sp
import shapefile as s


EARTH_RADIUS = 6378.137

def shapefile2geojson(fp):
    sf = s.Reader(fp)
    fields = sf.fields[1:]
    field_names = [field[0] for field in fields]
    features = []
    count = 0
    for sr in sf.shapeRecords():
        attr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        features.append({'type': 'Feature', 'geometry': geom, 'properties': attr, 'id': count})
        count += 1
    return {'type': 'FeatureCollection', 'features': features}

def get_net(s):
	lines = str(s).splitlines()
	line1 = lines[0]
	summary = line1.strip().split('#')
	node_num = int(summary[1])
	edge_num = int(summary[3])
	count = 0

	point_geojson = {
		"type": "FeatureCollection",
		"features": []
	}

	line_geojson = {
		"type": "FeatureCollection",
		"features": []
	}

	graph = sp.TUNGraph.New()

	points = {}

	while count < (node_num + edge_num):
		count += 1
		line = lines[count]
		if count <= node_num:
			node_els = line.strip().split('#')
			id = int(node_els[0])
			lon = float(node_els[1])
			lat = float(node_els[2])
			points[id] = [lon, lat]
			point_geojson['features'].append({
				"id": id,
				"type": "Feature",
				"geometry": {
					"type": "Point",
					"coordinates": [lon, lat]
				},
				"properties": {
					"seed": False,
					"diffused": -1
				}
			})
			graph.AddNode(id)
		else:
			edge_els = line.strip().split(',')
			edge_point1 = int(edge_els[0])
			edge_point2 = int(edge_els[1])
			line_geojson['features'].append(
				{
					"id": (count - node_num - 1),
					"type": "Feature",
					"geometry": {
						"type": "LineString",
						"coordinates": [ points[edge_point1], points[edge_point2] ]
					}
				}
			)
			graph.AddEdge(edge_point1, edge_point2)
	point_group = points.items()
	point_group.sort()
	point_list = [p[1] for p in point_group]
	return graph, point_list, point_geojson, line_geojson

def get_weights(s):
	return [[float(el) for el in line.strip().split('#')] for line in str(s).splitlines()]

# calculate the geographic distance based on two coordinates in degrees
def geo_distance(lat1, lon1, lat2, lon2):
	# degrees need to be converted into radians
	degree2rad = lambda d: np.pi * d / 180.0
	lat1_r = degree2rad(lat1)
	lat2_r = degree2rad(lat2)
	lon1_r = degree2rad(lon1)
	lon2_r = degree2rad(lon2)
	lat_diff = lat1_r - lat2_r
	lon_diff = lon1_r - lon2_r
	d = 2 * np.arcsin((np.sin(lat_diff / 2) ** 2 + np.sin(lon_diff / 2) ** 2 * np.cos(lat1_r) * np.cos(lat2_r)) ** .5)
	# the default unit is mile
	d *= EARTH_RADIUS / .621371
	return d

# independent cascade with locations "emergency_index" is of "list" and "decay_params" is of "dict"
def icm_by_locations(graph, seeds, weights, positions, emergency_type, emergency_index, terminations, decay_params=None):
	node_num = graph.GetNodes()
	# regional emergency requires computations on weights with decay effects
	if emergency_type == 'R':
		# 2d array of distances
		distances = np.full((node_num, node_num), 0)
		for i in range(node_num):
			for j in range(i + 1, node_num):
				d_params = np.array([positions[i], positions[j]]).flatten().tolist()
				d = geo_distance(*d_params)
				distances[i, j] = d
				distances[j, i] = d
		decay_radius = decay_params[0]
		decay_ratio = decay_params[1]
		# weights according to the decay effect
		weights = np.array(weights)
		weights *= ((1. - decay_ratio) ** (distances / decay_radius))
		weights = weights.tolist()
	# sort weights and acquire indexes to corresponding weights
	sorted_weights = [sorted(list(enumerate(weight_row)), key=lambda el: el[1], reverse=True) for weight_row in weights]
	sorted_w_indexes = [[el[0] for el in row] for row in sorted_weights]

	# run simulations based on different terminal modes
	terminal_type = terminations['type']

	# ensure activated, active, inactive nodes in three sets without intersections
	all_nodes = set([n.GetId() for n in graph.Nodes()])
	deactivated_nodes = set()
	active_nodes = set(seeds)
	prospective_nodes = all_nodes - deactivated_nodes - active_nodes

	results = []
	results.append([n for n in active_nodes])

	if terminal_type == 'step':
		max_steps = terminations['param']
		step_count = 0
		while step_count < max_steps and len(active_nodes) > 0 and len(prospective_nodes) > 0:
			current_index = emergency_index[step_count]
			current_seed = active_nodes.pop()
			deactivated_nodes.add(current_seed)
			candidate_nodes = sorted_w_indexes[current_seed]
			selected_nodes = candidate_nodes[:int(1 + current_index * node_num)]
			new_active_nodes = set(selected_nodes) - (deactivated_nodes | active_nodes)
			results.append(list(new_active_nodes))
			prospective_nodes = prospective_nodes - new_active_nodes
			active_nodes = active_nodes | new_active_nodes
			step_count += 1
	
	if terminal_type == 'coverage':
		max_coverage = terminations['param']
		accu_coverage = len(deactivated_nodes | active_nodes) / float(node_num)
		current_index = emergency_index[0]
		while accu_coverage < max_coverage and len(active_nodes) > 0 and len(prospective_nodes) > 0:
			current_seed = active_nodes.pop()
			deactivated_nodes.add(current_seed)
			candidate_nodes = sorted_w_indexes[current_seed]
			selected_nodes = candidate_nodes[:int(1 + current_index * node_num)]
			new_active_nodes = set(selected_nodes) - (deactivated_nodes | active_nodes)
			rest_node_num = int((max_coverage - accu_coverage) * node_num) + 1
			if rest_node_num >= len(new_active_nodes):
				results.append(list(new_active_nodes))
			else:
				results.append(list(new_active_nodes)[0:rest_node_num])
			prospective_nodes = prospective_nodes - new_active_nodes
			active_nodes = active_nodes | new_active_nodes
			accu_coverage = len(deactivated_nodes | active_nodes) / float(node_num)
	return results
