'''TODO:
    -need to create a celerybeat to check up on endpoints
    -need to parametize worker scripts
    -need to create a front end
    -need to finish the dockerfile crappiolioio

   Open thoughts:
    -Do i want to use redis as a broker
    -how in the world do i add authentication
'''



from flask_bootstrap import Bootstrap
import os 
import random
import time
from flask import Flask, request, render_template, session, flash, redirect, url_for, jsonify, g
from celery import Celery
import json
import requests
import configparser
from webapp import celeryconfig
from flask_restful import Resource, Api, reqparse
import shelve

app = Flask(__name__)
bs = Bootstrap(app)
api = Api(app)

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

#inititialize Shelf
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open("endpoints.db")
    print (db)
    return db

@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


#app single page
@app.route('/')
def index():
    return render_template('index.html')


#begin micro tasks
'''@celery.task(bind=True)
def get_json_pickle(self,payload):
    print (payload)
    keylist = []
    saved_pickle = payload['saved_pickle']
    pickle = payload['name']
    df = pd.read_pickle('/data/' + saved_pickle)
    df.to_pickle(pickle)
    htmlDF =  df.head(n=10).to_html().replace('<table border="1" class="dataframe">','<table class="table" id="dataframe">')
    for key in df.columns.values:
        meta = {'key':key}
        keylist.append(meta)
    result = [{'htmlDF':htmlDF,'keylist':keylist}]
    return({'result':htmlDF,'keylist':keylist})
    count = 0'''


class endpoints(Resource):
    def get(self):
        shelf = get_db()
        keys = list(shelf.keys())

        endpoints = []

        for key in keys:
            endpoints.append(shelf[key])

        return {'message': 'Success', 'data': endpoints}, 200

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('endpoint', required=True)
        parser.add_argument('worker_script', required=True)
        parser.add_argument('boolean', required=True)

        # Parse the arguments into an object
        args = parser.parse_args()

        shelf = get_db()
        shelf[args['endpoint']] = args

        return {'message': 'Device registered', 'data': args}, 201


class endpoint(Resource):
    def get(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Endpoint not found', 'data': {}}, 404

        return {'message': 'Endpoint found', 'data': shelf[identifier]}, 200

    def delete(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Endpoint not found', 'data': {}}, 404

        del shelf[identifier]
        return '', 204



@app.route('/apistatus/<task_id>')
def apistatus(task_id):
    task = get_json_from_api.AsyncResult(task_id)
    #print(task.info)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
            }
    return jsonify(response)


api.add_resource(endpoints, '/endpoints')
api.add_resource(endpoint, '/endpoint/<string:identifier>')


