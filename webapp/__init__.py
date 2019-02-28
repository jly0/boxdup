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
from flask_restful import Resource, Api, reqparse
import shelve
from . import celeryconfig

#initialize flask, celery
app = Flask(__name__)
bs = Bootstrap(app)
api = Api(app)
#app.config.from_object('config')

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
celery.config_from_object(celeryconfig)

#inititialize Shelf
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open("endpoints.db")
    print (db)
    return db

def extract_shelf_data():
    endpoints = []
    shelf = shelve.open('endpoints.db')
    for item in shelf:
        endpoints.append(shelf[item])
    return endpoints

@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


#app single page
@app.route('/')
def index():
    endpoints = extract_shelf_data()
    return render_template('index.html',endpoints=endpoints)


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
        parser.add_argument('workers', required=True)
        parser.add_argument('boolean', required=True)
        parser.add_argument('href', required=False)

        # Parse the arguments into an object
        args = parser.parse_args()

        shelf = get_db()
        shelf[args['endpoint']] = args

        return {'message': 'Endpoint registered', 'data': args}, 201


class endpoint(Resource):
    def get(self, endpoint):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (endpoint in shelf):
            return {'message': 'Endpoint not found', 'data': {}}, 404

        return {'message': 'Endpoint found', 'data': shelf[endpoint]}, 200

    def delete(self, identifier):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (identifier in shelf):
            return {'message': 'Endpoint not found', 'data': {}}, 404

        del shelf[identifier]
        return '', 204






api.add_resource(endpoints, '/endpoints')
api.add_resource(endpoint, '/endpoint/<string:endpoint>')