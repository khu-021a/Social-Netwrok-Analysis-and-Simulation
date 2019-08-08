import os
import re
import json
import uuid
import shutil
import random
import zipfile
import io
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, send_file, request, make_response
from pymongo import MongoClient
import geo
import transform
import networks as n
import diffusion as d
import utils as u


def create_app():
    # create and configure the app
    UPLOAD_FOLDER = './upload/'
    DOWNLOAD_FOLDER = './download/'
    SAMPLES_FOLDER = './samples/'
    COOKIE_KEY = 'user-id'
    COOKIE_DURATION = 1200
    if not os.path.exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.mkdir(DOWNLOAD_FOLDER)

    app = Flask(__name__, static_folder='assets')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    client = MongoClient('mongodb://localhost:27017/')
    user_records = client['network']['user_records']

    def update_modification_time(user_id):
        flag = user_records.update_one({
                'user': user_id
            }, {
                '$currentDate': {
                    'lastUpdate': { '$type': 'date' }
                }
            })
        return flag
    
    def assign_cookie_value(request, cookie_key):
        current_value = request.cookies.get(cookie_key)
        if current_value is None:
            new_value = str(uuid.uuid4())
            current_record = {
                'user': new_value,
                'network': None,
                'centralities': None,
                'communities': None,
                'diffusionUl': {
                    'seeds': None,
                    'opinionLeaders': None,
                    'seed_num': None,
                    'seed_alg': None,
                    'model': None,
                    'threshold': None,
                    'ol_scale': None,
                    'ol_ratio': None,
                    'ol_prob': None,
                    'norm_prob': None,
                    'results': None
                },
                'diffusionUlr': {
                    'seed_num': None,
                    'seed_alg': None,
                    'model': None,
                    'threshold': None,
                    'ol_scale': None,
                    'ol_ratio': None,
                    'ol_prob': None,
                    'norm_prob': None,
                    'results': None
                },
                'diffusionCl': {
                    'basemap': None,
                    'network': None,
                    'locations': None,
                    'weights': None,
                    'params': None,
                    'results': None
                },
                'lastUpdate': datetime.utcnow()
            }
            flag = user_records.insert_one(current_record)
            print flag
            return new_value
        else:
            flag = update_modification_time(current_value)
            print flag
            return current_value

    def bind_cookie(response, cookie_key, cookie_value, duration, no_cache=False):
        if no_cache:
            response.headers['Last-Modified'] = datetime.now()
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
        response.set_cookie(cookie_key, value=cookie_value, expires=(datetime.utcnow() + timedelta(seconds=duration)))
        return response
    
    # Index Page
    @app.route('/')
    def welcome():
        cookie_val = assign_cookie_value(request, COOKIE_KEY)
        print request.cookies
        response = make_response(send_from_directory('assets', 'index.html'), 200)
        return bind_cookie(response, COOKIE_KEY, cookie_val, COOKIE_DURATION)
    
    @app.route('/app')
    def home():
        cookie_val = assign_cookie_value(request, COOKIE_KEY)
        print request.cookies
        response = make_response(send_from_directory('assets', 'app.html'), 200)
        return bind_cookie(response, COOKIE_KEY, cookie_val, COOKIE_DURATION)
    
    @app.route('/doc')
    def document():
        user_id = assign_cookie_value(request, COOKIE_KEY)
        print request.cookies
        response = make_response(send_file('./manual.pdf', mimetype='application/pdf', as_attachment=True, attachment_filename='manual.pdf'), 200)
        return bind_cookie(response, COOKIE_KEY, user_id, COOKIE_DURATION, no_cache=True)
    
    @app.route('/generator/<string:net_type>', methods=['PUT'])
    def generate_network(net_type):
        if request.method == 'PUT':
            user_id = assign_cookie_value(request, COOKIE_KEY)
            print request.cookies
            raw_data = request.form
            data = json.loads(json.dumps(raw_data))
            if net_type == 'small-world':
                nodes = int(data['nodes'])
                outdegree = int(data['out-degree'])
                rewirepb = float(data['rewire-pb'])
                net = n.small_world(nodes, outdegree, rewirepb, rnd=(random.randint(1, 1e6), random.randint(1, 1e6)))
            elif net_type == 'pref-attach':
                nodes = int(data['nodes'])
                outdegree = int(data['out-degree'])
                net = n.pref_attach(nodes, outdegree, rnd=(random.randint(1, 1e6), random.randint(1, 1e6)))
            else:
                nodes = int(data['nodes'])
                edges = int(data['edges'])
                net = n.net_rnd(nodes, edges, rnd=(random.randint(1, 1e6), random.randint(1, 1e6)))
            net_dict = transform.graph2dict(net)
            communities = n.community_cnm(net)
            dc = n.degree_centrality(net)
            bc = n.betweenness_centrality(net)[0]
            cc = n.closeness_centrality(net)
            ec = n.eigenvector_centrality(net)
            dc_classes, dc_stats = u.node_centrality_equal_intervals(dc)
            bc_classes, bc_stats = u.node_centrality_equal_intervals(bc)
            cc_classes, cc_stats = u.node_centrality_equal_intervals(cc)
            ec_classes, ec_stats = u.node_centrality_equal_intervals(ec)
            net_dict['nodes'] = [{'id': node[0]['id'], 'dc': node[1], 'bc': node[2], 'cc': node[3], 'ec': node[4]} for node in zip(net_dict['nodes'], dc_classes, bc_classes, cc_classes, ec_classes)]
            net_dict = u.merge_results(net_dict, communities=communities)
            stored_centralities = [list(group) for group in  zip(bc, cc, dc, ec)]
            flag = user_records.update_one({
                    'user': user_id
                }, {
                    '$set': {
                        'network': net_dict,
                        'centralities': stored_centralities,
                        'communities': communities,
                    },
                    '$currentDate': {
                        'lastUpdate': { '$type': 'date' }
                    }
                })
            print flag
            response = make_response(json.dumps({'net': net_dict, 'dc': dc_stats, 'bc': bc_stats, 'cc': cc_stats, 'ec': ec_stats}), 200)
            return bind_cookie(response, COOKIE_KEY, user_id, COOKIE_DURATION)

    @app.route('/seeds', methods=['GET'])
    def get_seeds():
        if request.method == 'GET':
            user_id = assign_cookie_value(request, COOKIE_KEY)
            print request.cookies
            raw_data = request.args
            data = json.loads(json.dumps(raw_data))
            seed_num = int(data['seeds'])
            indicator = data['indicator']
            net_dict = user_records.find_one({'user': user_id}, {'network': 1, '_id': 0})
            if net_dict is None:
                results = {'error': 'A valid network has to be generated for this operation!'}
                flag = update_modification_time(user_id)
                response = make_response(json.dumps(results), 404)
            else:
                net = transform.dict2graph(net_dict['network'])
                seeds = n.seeds(net, seed_num, indicator)
                new_net = u.merge_results(net_dict['network'], seeds=seeds)
                flag = user_records.update_one({
                    'user': user_id
                }, {
                    '$set': {
                        'network': new_net,
                        'diffusionUl.seeds': seeds,
                        'diffusionUl.seed_num': seed_num,
                        'diffusionUl.seed_alg': indicator
                    },
                    '$currentDate': {
                        'lastUpdate': { '$type': 'date' }
                    }
                })
                print flag
                response = make_response(json.dumps(new_net), 200)
            return bind_cookie(response, COOKIE_KEY, user_id, COOKIE_DURATION)

    @app.route('/opinion-leaders', methods=['GET'])
    def get_transfer_sources():
        if request.method == 'GET':
            user_id = assign_cookie_value(request, COOKIE_KEY)
            print request.cookies
            raw_data = request.args
            data = json.loads(json.dumps(raw_data))
            ratio = float(data['ratio'])
            scale = data['scale']
            net_dict = user_records.find_one({'user': user_id}, {'network': 1, '_id': 0})
            if net_dict is None:
                results = {'error': 'A valid network has to be generated for this operation!'}
                flag = update_modification_time(user_id)
                response = make_response(json.dumps(results), 404)
            else:
                net = transform.dict2graph(net_dict['network'])
                if scale == 'R':
                    communities = user_records.find_one({'user': user_id}, {'communities': 1, '_id': 0})
                    if communities is None:
                        communities = n.community_cnm(net)
                        flag = user_records.update_one({
                            'user': user_id
                        }, {
                            '$set': {
                                'communities': communities
                            },
                            '$currentDate': {
                                'lastUpdate': { '$type': 'date' }
                            }
                        })
                        print flag
                    else:
                        communities = communities['communities']
                    opinion_leaders = n.find_transfer_sources(communities, ratio)
                else:
                    opinion_leaders = n.rnd_seeds(net.GetNodes(), int(net.GetNodes() * ratio))
                new_net = u.merge_results(net_dict['network'], opinion_leaders=opinion_leaders)
                flag = user_records.update_one({
                    'user': user_id
                }, {
                    '$set': {
                        'network': new_net,
                        'diffusionUl.opinionLeaders': opinion_leaders,
                        'diffusionUl.ol_scale': scale,
                        'diffusionUl.ol_ratio': ratio
                    },
                    '$currentDate': {
                        'lastUpdate': { '$type': 'date' }
                    }
                })
                print flag
                response = make_response(json.dumps(new_net), 200)
            return bind_cookie(response, COOKIE_KEY, user_id, COOKIE_DURATION)

    @app.route('/map-layers', methods=['PUT'])
    def load_basemap():
        if request.method == 'PUT':
            user_id = assign_cookie_value(request, COOKIE_KEY)
            print request.cookies
            raw_data = request.files
            files = dict(raw_data)
            current_dir = os.path.join(UPLOAD_FOLDER, user_id + '/')
            os.mkdir(current_dir)
            for f in files.values():
                name = f[0].filename
                content = f[0].read()
                if re.search('(.)+.shp$', name): 
                    shapefile_name = name
                with open(os.path.join(current_dir, name), 'wb') as local_f:
                    local_f.write(content)
            p = os.path.join(current_dir, shapefile_name)
            geojson = geo.shapefile2geojson(p)
            shutil.rmtree(current_dir)
            flag = user_records.update_one({
                    'user': user_id
                }, {
                    '$set': {
                        'diffusionCl.basemap': json.dumps(geojson)
                    },
                    '$currentDate': {
                        'lastUpdate': { '$type': 'date' }
                    }
                })
            print flag
            response = make_response(json.dumps(geojson), 200)
            return bind_cookie(response, COOKIE_KEY, user_id, COOKIE_DURATION)

    @app.route('/net-file', methods=['PUT'])
    def load_net():
        if request.method == 'PUT':
            user_id = assign_cookie_value(request, COOKIE_KEY)
            print request.cookies
            raw_data = request.files
            files = dict(raw_data)
            f = files.values()[0][0]
            content = f.read()
            graph, positions, point, line = geo.get_net(content)
            f.close()
            flag = user_records.update_one({
                    'user': user_id
                }, {
                    '$set': {
                        'diffusionCl.network': transform.graph2dict(graph),
                        'diffusionCl.locations': positions
                    },
                    '$currentDate': {
                        'lastUpdate': { '$type': 'date' }
                    }
                })
            print flag
            response = make_response(json.dumps({'point': point, 'line': line}), 200)
            return bind_cookie(response, COOKIE_KEY, user_id, COOKIE_DURATION)

    @app.route('/weight-file', methods=['PUT'])
    def load_weights():
        if request.method == 'PUT':
            user_id = assign_cookie_value(request, COOKIE_KEY)
            print request.cookies
            raw_data = request.files
            files = dict(raw_data)
            f = files.values()[0][0]
            content = f.read()
            matrix = geo.get_weights(content)
            f.close()
            flag = user_records.update_one({
                    'user': user_id
                }, {
                    '$set': {
                        'diffusionCl.weights': matrix
                    },
                    '$currentDate': {
                        'lastUpdate': { '$type': 'date' }
                    }
                })
            print flag
            response = make_response(json.dumps({'msg': 'Weight matrix is received!'}), 200)
            return bind_cookie(response, COOKIE_KEY, user_id, COOKIE_DURATION)
    
    @app.route('/diffusion-ul', methods=['GET'])
    def diffuse_ul():
        if request.method == 'GET':
            user_id = assign_cookie_value(request, COOKIE_KEY)
            print request.cookies
            raw_data = request.args
            data = json.loads(json.dumps(raw_data))
            model_type = data['model']
            seed_num = int(data['seeds'])
            indicator = data['indicator']
            net_dict = user_records.find_one({'user': user_id}, {'network': 1, '_id': 0})
            seeds = user_records.find_one({'user': user_id}, {'diffusionUl.seeds': 1, '_id': 0})
            if net_dict is None:
                results = {'error': 'A valid network has to be generated for this operation!'}
                flag = update_modification_time(user_id)
                response = make_response(json.dumps(results), 404)
            else:
                net = transform.dict2graph(net_dict['network'])
                seeds = n.seeds(net, seed_num, indicator) if seeds is None else seeds['diffusionUl']['seeds']
                
                if model_type == 'ltm':
                    threshold = float(data['threshold'])
                    diffused = d.LTM(net, seeds, threshold)
                    new_net = u.merge_results(net_dict['network'], seeds=seeds, opinion_leaders=None, communities=None, diffused=diffused)
                    flag = user_records.update_one({
                        'user': user_id
                    }, {
                        '$set': {
                            'diffusionUl':{
                                'seeds': seeds,
                                'opinionLeaders': None,
                                'model': model_type,
                                'seed_num': seed_num,
                                'seed_alg': indicator,
                                'threshold': threshold,
                                'ol_scale': None,
                                'ol_ratio': None,
                                'ol_prob': None,
                                'norm_prob': None,
                                'results': diffused
                            }
                        },
                        '$currentDate': {
                            'lastUpdate': { '$type': 'date' }
                        }
                    })
                    print flag
                if model_type == 'icm':
                    pb_leaders = float(data['pb-leaders'])
                    pb_normal = float(data['pb-normal'])
                    scale = data['scale']
                    ratio = float(data['ratio'])

                    communities = user_records.find_one({'user': user_id}, {'communities': 1, '_id': 0})
                    opinion_leaders = user_records.find_one({'user': user_id}, {'diffusionUl.opinionLeaders': 1, '_id': 0})

                    if communities is None:
                        communities = n.community_cnm(net)
                        flag = user_records.update_one({
                            'user': user_id
                        }, {
                            '$set': {
                                'communities': communities
                            },
                            '$currentDate': {
                                'lastUpdate': { '$type': 'date' }
                            }
                        })
                        print flag
                    else:
                        communities = communities['communities']
                    
                    if opinion_leaders is None:
                        if scale == 'R':
                            opinion_leaders = n.find_transfer_sources(communities, ratio)
                        else:
                            opinion_leaders = n.rnd_seeds(net.GetNodes(), int(net.GetNodes() * ratio))
                        flag = user_records.update_one({
                            'user': user_id
                        }, {
                            '$set': {
                                'diffusionUl.opinionLeaders': opinion_leaders
                            },
                            '$currentDate': {
                                'lastUpdate': { '$type': 'date' }
                            }
                        })
                        print flag
                    else:
                        opinion_leaders = opinion_leaders['diffusionUl']['opinionLeaders']
                    
                    diffused = d.ICM(net, seeds, opinion_leaders, pb_leaders, pb_normal)
                    new_net = u.merge_results(net_dict['network'], seeds=seeds, opinion_leaders=opinion_leaders, communities=communities, diffused=diffused)
                    flag = user_records.update_one({
                        'user': user_id
                    }, {
                        '$set': {
                            'diffusionUl':{
                                'seeds': seeds,
                                'opinionLeaders': opinion_leaders,
                                'model': model_type,
                                'seed_num': seed_num,
                                'seed_alg': indicator,
                                'threshold': None,
                                'ol_scale': scale,
                                'ol_ratio': ratio,
                                'ol_prob': pb_leaders,
                                'norm_prob': pb_normal,
                                'results': diffused
                            }
                        },
                        '$currentDate': {
                            'lastUpdate': { '$type': 'date' }
                        }
                    })
                    print flag
                flag = update_modification_time(user_id)
                response = make_response(json.dumps(new_net), 200)
                
            return bind_cookie(response, COOKIE_KEY, user_id, COOKIE_DURATION)

    @app.route('/diffusion-ulr/<string:model_type>', methods=['GET'])
    def batch_ulr(model_type):
        if request.method == 'GET':
            user_id = assign_cookie_value(request, COOKIE_KEY)
            print request.cookies
            raw_data = request.args
            #print data
            net_dict = user_records.find_one({'user': user_id}, {'network': 1, '_id': 0})
            net = transform.dict2graph(net_dict['network'])
            total_node_num = net.GetNodes()
            if model_type == 'ltm':
                data = json.loads(json.dumps(raw_data))
                min_seeds = int(data['minSeeds'])
                max_seeds = int(data['maxSeeds'])
                s_range_num = int(data['seedRangeNum'])
                seed_alg = data['seedAlg']
                min_thres = float(data['minThres'])
                max_thres = float(data['maxThres'])
                t_range_num = int(data['thresRangeNum'])
                #seeds part
                s_diff = max_seeds - min_seeds
                s_step = 1.0 * s_diff / s_range_num
                s_step_int = int(s_step) if s_step > 1 else 1
                s_nums = range(min_seeds, max_seeds, s_step_int)
                if s_nums[-1] != max_seeds:
                    s_nums.append(max_seeds)
                all_seeds = [n.seeds(net, s, seed_alg) for s in s_nums]
                #thresholds part
                t_diff = max_thres - min_thres
                t_step = t_diff / t_range_num
                all_thres = [(min_thres + num * t_step) for num in range(t_range_num)]
                if all_thres[-1] != max_thres:
                    all_thres.append(max_thres)
                ltm_args_list = [{'seeds': s, 'threshold': t} for s in all_seeds for t in all_thres]
                direct_results = [d.LTM(net, **args) for args in ltm_args_list]
                all_results = [len(u.flatten_list_2d(result)) * 1.0 / total_node_num for result in direct_results]
                ltm_info = {'x-field': 'Seed Number', 'y-field': 'Threshold', 'x': {'min': s_nums[0], 'max': s_nums[-1]}, 'y': {'min': all_thres[0], 'max': all_thres[-1]}}
                ltm_results = [[len(group[0]['seeds']), group[0]['threshold'], group[1]] for group in zip(ltm_args_list, all_results)]
                flag = user_records.update_one({
                    'user': user_id
                }, {
                    '$set': {
                        'diffusionUlr': {
                            'seed_num': [min_seeds, max_seeds, s_range_num],
                            'seed_alg': seed_alg,
                            'model': model_type,
                            'threshold': [min_thres, max_thres, t_range_num],
                            'ol_scale': None,
                            'ol_ratio': None,
                            'ol_prob': None,
                            'norm_prob': None,
                            'results': {'diffused': direct_results, 'stats': all_results}
                        }
                    },
                    '$currentDate': {
                        'lastUpdate': { '$type': 'date' }
                    }
                })
                print flag
                #flag = update_modification_time(user_id)
                response = make_response(json.dumps({'info': ltm_info, 'data': ltm_results}), 200)
            if model_type == 'icm':
                data = json.loads(raw_data['data'])
                seeds = data['seeds']
                op_prob = data['op-prob']
                n_prob = data['n-prob']
                op_ratio = data['op-ratio']
                scale = data['scale']
                alg = data['alg']
                args_flags = {'seeds': 0, 'transfer_sources': 0, 'pb_source': 0, 'pb_normal': 0}
                def get_range_list(d, int_step=False):
                    min_val = d['min']
                    max_val = d['max']
                    n_range = d['rn']
                    step = 1.0 * (max_val - min_val) / n_range
                    if int_step:
                        step = int(step) if step > 1 else 1
                        nums = range(min_val, max_val, step)
                    else:
                        nums = [(min_val + num * step) for num in range(n_range)]
                    if nums[-1] != max_val:
                        nums.append(max_val)
                    return nums
                if isinstance(seeds, dict): 
                    s_nums = get_range_list(seeds, True)
                    args_flags['seeds'] = 1
                else:
                    s_nums = [seeds]
                seed_sets = [n.seeds(net, s, alg) for s in s_nums]
                if isinstance(op_ratio, dict): 
                    opr_nums = get_range_list(op_ratio)
                    args_flags['transfer_sources'] = 2
                else:
                    opr_nums = [op_ratio]
                transfer_sources = [n.find_opinion_leaders(net, scale, r) for r in opr_nums]
                if isinstance(op_prob, dict): 
                    op_probs = get_range_list(op_prob)
                    args_flags['pb_source'] = 3
                else:
                    op_probs = [op_prob]
                if isinstance(n_prob, dict): 
                    n_probs = get_range_list(n_prob)
                    args_flags['pb_normal'] = 4
                else:
                    n_probs = [n_prob]
                
                ranged_fields = [k for k, v in args_flags.items() if v > 0]
                if args_flags[ranged_fields[0]] < args_flags[ranged_fields[1]]:
                    x_axis = ranged_fields[0]
                    y_axis = ranged_fields[1]
                else:
                    x_axis = ranged_fields[1]
                    y_axis = ranged_fields[0]
                if x_axis == 'seeds':
                    x_title = 'Seed Number'
                    x_info = {'min': seeds['min'], 'max': seeds['max']}
                    x_range = [s for s in s_nums]
                if x_axis == 'transfer_sources':
                    x_title = 'Opinion Leader Number'
                    x_info = {'min': op_ratio['min'], 'max': op_ratio['max']}
                    x_range = [on for on in opr_nums]
                if x_axis == 'pb_source':
                    x_title = 'Opinion Leader Probability'
                    x_info = {'min': op_prob['min'], 'max': op_prob['max']}
                    x_range = [opb for opb in op_probs]
                if y_axis == 'transfer_sources':
                    y_title = 'Opinion Leader Number'
                    y_info = {'min': op_ratio['min'], 'max': op_ratio['max']}
                    y_range = [on for on in opr_nums]
                if y_axis == 'pb_source':
                    y_title = 'Opinion Leader Probability'
                    y_info = {'min': op_prob['min'], 'max': op_prob['max']}
                    y_range = [opb for opb in op_probs]
                if y_axis == 'pb_normal':
                    y_title = 'Opinion Leader Probability'
                    y_info = {'min': n_prob['min'], 'max': n_prob['max']}
                    y_range = [npb for npb in n_probs]
                
                icm_args_list = [{'seeds': ss, 'transfer_sources': ts, 'pb_source': opb, 'pb_normal': npb} for ss in seed_sets for ts in transfer_sources for opb in op_probs for npb in n_probs]
                direct_results = [d.ICM(net, **args) for args in icm_args_list]
                all_results = [len(u.flatten_list_2d(result)) * 1.0 / total_node_num for result in direct_results]
                
                icm_info = {'x-field': x_title, 'y-field': y_title, 'x': x_info, 'y': y_info}
                icm_results = [[group[0][0], group[0][1], group[1]] for group in zip([(x, y) for x in x_range for y in y_range], all_results)]
                flag = user_records.update_one({
                    'user': user_id
                }, {
                    '$set': {
                        'diffusionUlr': {
                            'seed_num': [seeds['min'], seeds['max'], seeds['rn']] if isinstance(seeds, dict) else int(seeds),
                            'seed_alg': alg,
                            'model': model_type,
                            'threshold': None,
                            'ol_scale': scale,
                            'ol_ratio': [op_ratio['min'], op_ratio['max'], op_ratio['rn']] if isinstance(op_ratio, dict) else float(op_ratio),
                            'ol_prob': [op_prob['min'], op_prob['max'], op_prob['rn']] if isinstance(op_prob, dict) else float(op_prob),
                            'norm_prob': [n_prob['min'], n_prob['max'], n_prob['rn']] if isinstance(n_prob, dict) else float(n_prob),
                            'results': {'diffused': direct_results, 'stats': all_results}
                        }
                    },
                    '$currentDate': {
                        'lastUpdate': { '$type': 'date' }
                    }
                })
                print flag
                #flag = update_modification_time(user_id)
                response = make_response(json.dumps({'info': icm_info, 'data': icm_results}), 200)
            return bind_cookie(response, COOKIE_KEY, user_id, COOKIE_DURATION)
    
    @app.route('/diffusion-cl', methods=['GET'])
    def diffuse_cl():
        if request.method == 'GET':
            user_id = assign_cookie_value(request, COOKIE_KEY)
            print request.cookies
            raw_data = request.args
            data = json.loads(json.loads(json.dumps(raw_data))['data'])
            sources = data['sources']
            termination = data['termination']
            urgency_type = data['urgency-type']
            urgency_vals = data['urgency-values']
            decay_params = data['decay-params']
            all_params = {
                'source_cities': sources,
                'termination': termination,
                'urgency': {
                    'type': urgency_type,
                    'values': urgency_vals
                },
                'decay': decay_params
            }
            flag = user_records.update_one({
                'user': user_id
            }, {
                '$set': {
                    'diffusionCl.params': all_params
                },
                '$currentDate': {
                    'lastUpdate': { '$type': 'date' }
                }
            })
            print flag
            net_dict = user_records.find_one({'user': user_id}, {'diffusionCl.network': 1, '_id': 0})
            locations = user_records.find_one({'user': user_id}, {'diffusionCl.locations': 1, '_id': 0})
            weights = user_records.find_one({'user': user_id}, {'diffusionCl.weights': 1, '_id': 0})
            if net_dict is None or locations is None:
                results = {'error': 'A valid network or relative locations have to be generated for this operation!'}
                flag = update_modification_time(user_id)
                print flag
                response = make_response(json.dumps(results), 404)
            elif weights is None:
                results = {'error': 'Weight matrix has to be generated for this operation!'}
                flag = update_modification_time(user_id)
                print flag
                response = make_response(json.dumps(results), 404)
            else:
                net = transform.dict2graph(net_dict['diffusionCl']['network'])
                location_list = locations['diffusionCl']['locations']
                weight_matrix = weights['diffusionCl']['weights']
                results = geo.icm_by_locations(net, sources, weight_matrix, location_list, urgency_type, urgency_vals, termination, decay_params)
                print results
                node_num = net.GetNodes()
                num_in_step = [len(nodes) for nodes in results]
                acc_ratio_in_step = [num * 100.0 / node_num for num in u.get_acc_list(num_in_step)]
                response_results = {
                    'diffusion': u.list2d2dict(u.preprocess_cl_results(results)), 
                    'statistics': {
                        'num_in_step': num_in_step,
                        'ratio_in_step': acc_ratio_in_step
                    }
                }
                stored_results = zip(num_in_step, acc_ratio_in_step, results)
                flag = user_records.update_one({
                    'user': user_id
                }, {
                    '$set': {
                        'diffusionCl.results': stored_results
                    },
                    '$currentDate': {
                        'lastUpdate': { '$type': 'date' }
                    }
                })
                print flag
                response = make_response(json.dumps(response_results), 200)
            return bind_cookie(response, COOKIE_KEY, user_id, COOKIE_DURATION)

    @app.route('/export-network')
    def download_network():
        user_id = assign_cookie_value(request, COOKIE_KEY)
        print request.cookies
        dir_name = user_id + '-' + datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%SZ')
        current_dir = os.path.join(DOWNLOAD_FOLDER, dir_name + '/')
        os.mkdir(current_dir)
        net_ul = user_records.find_one({'user': user_id}, {'network': 1, '_id': 0})
        nodes = [str(x['id']) for x in net_ul['network']['nodes']]
        edges = [(str(e['source']), str(e['target'])) for e in net_ul['network']['edges']]
        line1 = 'Nodes#' + str(len(nodes)) + '#Edges#' + str(len(edges)) + '\n'
        node_lines = '\n'.join(nodes) + '\n'
        edge_lines = '\n'.join([e[0] + ',' + e[1] for e in edges]) + '\n'
        all_lines = line1 + node_lines + edge_lines

        with open(os.path.join(current_dir, 'net.txt'), 'w') as f:
            f.write(all_lines)
        
        file_paths = []
        for root, _, files in os.walk(current_dir): 
            for filename in files: 
                # join the two strings in order to form the full filepath. 
                filepath = os.path.join(root, filename) 
                file_paths.append(filepath) 

        data = io.BytesIO()
        with zipfile.ZipFile(data, mode='w') as z:
            for f_name in file_paths:
                z.write(f_name)
        data.seek(0)
        shutil.rmtree(current_dir)
        update_modification_time(user_id)
        response = make_response(send_file(data, mimetype='application/zip', as_attachment=True, attachment_filename='network.zip'), 200)
        return bind_cookie(response, COOKIE_KEY, user_id, COOKIE_DURATION, no_cache=True)
    
    @app.route('/export-analysis')
    def download_analysis():
        user_id = assign_cookie_value(request, COOKIE_KEY)
        print request.cookies
        dir_name = user_id + '-' + datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%SZ')
        current_dir = os.path.join(DOWNLOAD_FOLDER, dir_name + '/')
        os.mkdir(current_dir)
        indicators = user_records.find_one({'user': user_id}, {'centralities': 1, 'communities': 1, '_id': 0})
        centralities = indicators['centralities']
        communities = sorted(u.list2d2dict(indicators['communities']).items())
        results_content = 'id,community,bc,cc,dc,ec' + '\n'
        results_content += ''.join([','.join(map(str, c1) + map(str, c2)) + '\n' for c1, c2 in zip(communities, centralities)])
        with open(os.path.join(current_dir, 'analysis.csv'), 'w') as f:
            f.write(results_content)
        
        file_paths = []
        for root, _, files in os.walk(current_dir): 
            for filename in files: 
                # join the two strings in order to form the full filepath. 
                filepath = os.path.join(root, filename) 
                file_paths.append(filepath) 

        data = io.BytesIO()
        with zipfile.ZipFile(data, mode='w') as z:
            for f_name in file_paths:
                z.write(f_name)
        data.seek(0)
        shutil.rmtree(current_dir)
        update_modification_time(user_id)
        response = make_response(send_file(data, mimetype='application/zip', as_attachment=True, attachment_filename='analysis.zip'), 200)
        return bind_cookie(response, COOKIE_KEY, user_id, COOKIE_DURATION, no_cache=True)

    @app.route('/export-ul')
    def download_ul():
        user_id = assign_cookie_value(request, COOKIE_KEY)
        print request.cookies
        dir_name = user_id + '-' + datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%SZ')
        current_dir = os.path.join(DOWNLOAD_FOLDER, dir_name + '/')
        os.mkdir(current_dir)
        ul_records = user_records.find_one({'user': user_id}, {'diffusionUl': 1, '_id': 0})['diffusionUl']
        param_lines = []
        param_lines.append('param_name,param_value')
        model = ul_records['model']
        param_lines.append('model,' + model)
        param_lines.append('seed_alg,' + ul_records['seed_alg'])
        param_lines.append('seed_num,' + str(ul_records['seed_num']))
        results = ul_records['results']
        if model == 'ltm':
            param_lines.append('threshold,' + str(ul_records['threshold']))
        if model == 'icm':
            param_lines.append('ol_scale,' + str(ul_records['ol_scale']))
            param_lines.append('ol_ratio,' + str(ul_records['ol_ratio']))
            param_lines.append('ol_prob,' + str(ul_records['ol_prob']))
            param_lines.append('norm_prob,' + str(ul_records['norm_prob']))
        result_lines = [str(i) + ',[' + ' '.join(map(str, r)) + ']' for i, r in enumerate(results)]
        result_lines.insert(0, 'iter_num,diffused')
        with open(os.path.join(current_dir, 'ul_params.csv'), 'w') as f:
            f.writelines(map(lambda l: l + '\n', param_lines))
        with open(os.path.join(current_dir, 'ul_results.csv'), 'w') as f:
            f.writelines(map(lambda l: l + '\n', result_lines))
        file_paths = []
        for root, _, files in os.walk(current_dir): 
            for filename in files: 
                filepath = os.path.join(root, filename) 
                file_paths.append(filepath) 

        data = io.BytesIO()
        with zipfile.ZipFile(data, mode='w') as z:
            for f_name in file_paths:
                z.write(f_name)
        data.seek(0)
        shutil.rmtree(current_dir)
        update_modification_time(user_id)
        response = make_response(send_file(data, mimetype='application/zip', as_attachment=True, attachment_filename='ul_results.zip'), 200)
        return bind_cookie(response, COOKIE_KEY, user_id, COOKIE_DURATION, no_cache=True)

    @app.route('/export-ulr')
    def download_ulr():
        user_id = assign_cookie_value(request, COOKIE_KEY)
        print request.cookies
        dir_name = user_id + '-' + datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%SZ')
        current_dir = os.path.join(DOWNLOAD_FOLDER, dir_name + '/')
        os.mkdir(current_dir)
        ulr_records = user_records.find_one({'user': user_id}, {'diffusionUlr': 1, '_id': 0})['diffusionUlr']
        param_lines = []
        param_lines.append('param_name,param_value')
        model = ulr_records['model']
        param_lines.append('model,' + model)
        param_lines.append('seed_alg,' + ulr_records['seed_alg'])
        param_lines.append('seed_num,' + (('[' + ' '.join(map(str, ulr_records['seed_num'])) + ']') if isinstance(ulr_records['seed_num'], list) else str(ulr_records['seed_num'])))
        results = ulr_records['results']
        if model == 'ltm':
            param_lines.append('threshold,' + (('[' + ' '.join(map(str, ulr_records['threshold'])) + ']') if isinstance(ulr_records['threshold'], list) else str(ulr_records['threshold'])))
        if model == 'icm':
            param_lines.append('ol_scale,' + str(ulr_records['ol_scale']))
            param_lines.append('ol_ratio,' + (('[' + ' '.join(map(str, ulr_records['ol_ratio'])) + ']') if isinstance(ulr_records['ol_ratio'], list) else str(ulr_records['ol_ratio'])))
            param_lines.append('ol_prob,' + (('[' + ' '.join(map(str, ulr_records['ol_prob'])) + ']') if isinstance(ulr_records['ol_prob'], list) else str(ulr_records['ol_prob'])))
            param_lines.append('norm_prob,' + (('[' + ' '.join(map(str, ulr_records['norm_prob'])) + ']') if isinstance(ulr_records['norm_prob'], list) else str(ulr_records['norm_prob'])))
        result_lines = [r1 + ',' + r2 for r1, r2 in zip(['[' + ' '.join(['[' + ' '.join([str(z)for z in y]) + ']' for y in x]) + ']' for x in results['diffused']], map(str, results['stats']))]
        result_lines.insert(0, 'diffused,diffused_ratio')
        with open(os.path.join(current_dir, 'ulr_params.csv'), 'w') as f:
            f.writelines(map(lambda l: l + '\n', param_lines))
        with open(os.path.join(current_dir, 'ulr_results.csv'), 'w') as f:
            f.writelines(map(lambda l: l + '\n', result_lines))
        file_paths = []
        for root, _, files in os.walk(current_dir): 
            for filename in files: 
                filepath = os.path.join(root, filename) 
                file_paths.append(filepath) 

        data = io.BytesIO()
        with zipfile.ZipFile(data, mode='w') as z:
            for f_name in file_paths:
                z.write(f_name)
        data.seek(0)
        shutil.rmtree(current_dir)
        update_modification_time(user_id)
        response = make_response(send_file(data, mimetype='application/zip', as_attachment=True, attachment_filename='ulr_results.zip'), 200)
        return bind_cookie(response, COOKIE_KEY, user_id, COOKIE_DURATION, no_cache=True)

    @app.route('/export-cl')
    def download_cl():
        user_id = assign_cookie_value(request, COOKIE_KEY)
        print request.cookies
        dir_name = user_id + '-' + datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%SZ')
        current_dir = os.path.join(DOWNLOAD_FOLDER, dir_name + '/')
        os.mkdir(current_dir)
        params = user_records.find_one({'user': user_id}, {'diffusionCl.params': 1, '_id': 0})
        params = params['diffusionCl']['params']
        params_content = 'param_name,param_value' + '\n'
        params_content += 'source_cities,[' + ' '.join([str(c) for c in params['source_cities']]) + ']' + '\n'
        params_content += 'termination_type,' + params['termination']['type'] + '\n'
        params_content += 'termination_value,' + str(params['termination']['param']) + '\n'
        params_content += 'urgency_type,' + params['urgency']['type'] + '\n'
        params_content += 'urgency_values,[' + ' '.join([str(v) for v in params['urgency']['values']]) + ']' + '\n'
        if params['urgency']['type'] == 'R':
            params_content += 'decay_radius,' + str(params['decay'][0]) + '\n'
            params_content += 'decay_ratio,' + str(params['decay'][1]) + '\n'
        results = user_records.find_one({'user': user_id}, {'diffusionCl.results': 1, '_id': 0})
        results = results['diffusionCl']['results']
        results_content = 'step_num,active_node_num,acc_node_ratio,active_node_in_step' + '\n'
        for i, v in enumerate(results):
            results_content += ','.join([str(i), str(v[0]), str(v[1]), '[' + ' '.join([str(k) for k in v[2]]) + ']']) + '\n'
        with open(os.path.join(current_dir, 'cl_params.csv'), 'w') as f:
            f.write(params_content)
        with open(os.path.join(current_dir, 'cl_results.csv'), 'w') as f:
            f.write(results_content)
        
        file_paths = []
        for root, _, files in os.walk(current_dir): 
            for filename in files: 
                filepath = os.path.join(root, filename) 
                file_paths.append(filepath) 

        data = io.BytesIO()
        with zipfile.ZipFile(data, mode='w') as z:
            for f_name in file_paths:
                z.write(f_name)
        data.seek(0)
        shutil.rmtree(current_dir)
        update_modification_time(user_id)
        response = make_response(send_file(data, mimetype='application/zip', as_attachment=True, attachment_filename='cl_results.zip'), 200)
        return bind_cookie(response, COOKIE_KEY, user_id, COOKIE_DURATION, no_cache=True)

    @app.route('/download-samples')
    def download_cl_samples():
        user_id = assign_cookie_value(request, COOKIE_KEY)
        print request.cookies
        file_paths = []
        for root, _, files in os.walk(SAMPLES_FOLDER): 
            for filename in files: 
                filepath = os.path.join(root, filename) 
                file_paths.append(filepath) 

        data = io.BytesIO()
        with zipfile.ZipFile(data, mode='w') as z:
            for f_name in file_paths:
                z.write(f_name)
        data.seek(0)
        #shutil.rmtree(SAMPLES_FOLDER)
        update_modification_time(user_id)
        response = make_response(send_file(data, mimetype='application/zip', as_attachment=True, attachment_filename='cl_samples.zip'), 200)
        return bind_cookie(response, COOKIE_KEY, user_id, COOKIE_DURATION, no_cache=True)
    
    return app
