

import os
import json
from flask import Flask
from flask import send_from_directory
from flask import request
import importlib
import networkx as nx 
import difsim 
import graph
import datatransfer
import snap
import seeds

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Index Page
    @app.route('/')
    def index():
        return send_from_directory('templates', 'base.html')
    
    @app.route('/smallworld', methods=['POST'])
    def smallworld():
        if request.method == 'POST':
            raw_data = request.form
            print(raw_data)
            print(json.dumps(raw_data))
            data = json.loads(json.dumps(raw_data))
            print(data)
            print(type(data['nodes']))
            nodes = int(data['nodes'])
            outdegree = int(data['outdegree'])
            rewirepb = float(data['rewirepb'])
            
            s1 = graph.samllworld_gnm(nodes, outdegree, rewirepb)
            #datatransfer.datatransfer(s1)
            #print(s1)
            return json.dumps(datatransfer.datatransfer(s1))
    
    @app.route('/PrefAttach', methods=['POST'])
    def prefattach():
        if request.method == 'POST':
            raw_data = request.form
            print(raw_data)
            data = json.loads(json.dumps(raw_data))
            nodes = int(data['nodes'])
            outdegree = int(data['outdegree'])
            
            s1 = graph.prefattach_gnm(nodes, outdegree)
            #datatransfer.datatransfer(s1)
            return json.dumps(datatransfer.datatransfer(s1))

    @app.route('/Random', methods=['POST'])
    def rand():
        if request.method == 'POST':
            raw_data = request.form
            print(raw_data)
            data = json.loads(json.dumps(raw_data))
            nodes = int(data['nodes'])
            edges = int(data['edges'])
            
            s1 = graph.rnd_gnm(snap.PNGraph,nodes, edges)
            #datatransfer.datatransfer(s1)
            return json.dumps(datatransfer.datatransfer(s1))
    
    @app.route('/seednodes', methods=['PUT'])
    def seednodes():
        if request.method == 'PUT':
            raw_data = request.form
            print(raw_data)
            data = json.loads(json.dumps(raw_data))
            seednodes = int(data['seednodes'])
            algorithm = data['algorithm']
            
            s1 = graph.samllworld_gnm(100, 5, .15)
            seed_nodes = seeds.seeds(s1,seednodes,algorithm)
            #--datatransfer.datatransfer(s1,seed_nodes)
            results = datatransfer.datatransfer(s1,seed_nodes,[1, 2])
            print(results)
            return json.dumps(results)
        
    return app

