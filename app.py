import os
import json
import datetime
import uuid
import requests
from flask import Flask, jsonify, request, Response, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from routing_functions import Routing_functions
from authorization import *
from validation import *


#create flask app and configure
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://'+os.getenv('POSTGRES_RESERVATIONS_USER')+':'+os.getenv('POSTGRES_RESERVATIONS_PASSWORD')+'@'+os.getenv('POSTGRES_RESERVATIONS_HOST')+':'+os.getenv('POSTGRES_RESERVATIONS_PORT')+'/'+os.getenv('POSTGRES_RESERVATIONS_DBNAME')+''
db = SQLAlchemy(app)


#Defining the Routes
@app.route("/reservations/status/", methods=['GET'])
def reservations_status():
    
    return Routing_functions.reservations_status()

@app.route("/reservations/", methods=['GET', 'POST'])
def reservations():
    #POST Request
    if request.method == 'POST':
        # get auth token from header
        
        return Routing_functions.post_reservations(request)
    #GET Request
    if request.method == 'GET':
        
        return Routing_functions.get_reservations(request)
        
        
        
        
@app.route("/reservations/<input_id>/", methods=['GET', 'PUT', 'DELETE'])
def reservations_byID(input_id: str): 
    #GET request
    if request.method == 'GET':
        
        return Routing_functions.get_reservation_by_id(input_id)

    #PUT request
    elif request.method == 'PUT':
        
        return Routing_functions.put_reservation_by_id(input_id,request) 
        
    #DELETE request
    else:
        
        return Routing_functions.delete_reservation_by_id(input_id,request) 
        

if __name__ == '__main__':
    #import custom db scheme
    from database import reservations
    with app.app_context(): 
        db.create_all()
    #define the localhost ip and the port that is going to be used
    app.run(host=os.getenv('HOST'), port=os.getenv('PORT'), debug=True)