
#! python3

import os
import json
from flask import Flask
from flask import send_from_directory
from flask import request

#from networks.difsim import difsim 

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
    
    @app.route('/simulator1', methods=['POST'])
    def simulator():
        if request.method == 'POST':
            data = json.loads(json.dumps(request.form))
            nodes = int(data['nodes'])
            edges = int(data['edges'])
            infected = float(data['infected'])
            threshold = float(data['threshold'])
            iteration = int(data['iteration'])
            #s1 = difsim(nodes, edges, infected, threshold, iteration)
            #print(s1)
            #return s1
            
    return app

