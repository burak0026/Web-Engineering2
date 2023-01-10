import os
import json
import datetime
import uuid
import requests
from flask import Flask, jsonify, request, Response, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID

from authorization import *
from validation import *


#create flask app and configure
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://'+os.getenv('POSTGRES_RESERVATIONS_USER')+':'+os.getenv('POSTGRES_RESERVATIONS_PASSWORD')+'@'+os.getenv('POSTGRES_RESERVATIONS_HOST')+':'+os.getenv('POSTGRES_RESERVATIONS_PORT')+'/'+os.getenv('POSTGRES_RESERVATIONS_DBNAME')+''
db = SQLAlchemy(app)


#Defining the Routes
@app.route("/reservations/status/", methods=['GET'])
def reservations_status():
    app.logger.info('Get Statusinformation')
    return {
        "authors": "Burak Oezkan, Marius Engelmeier",
        "apiVersion": "1.0"
        }

@app.route("/reservations/", methods=['GET', 'POST'])
def reservations_general():
    
    #POST Request
    if request.method == 'POST':
        # get auth token from header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = None
        #validate token
        resp = validate_jwt(auth_token)
        if resp is not True:
            return resp
        #get Values from Message Body
        content = request.json
        #validate JSON-Content values
        if checkJSONValues(content) is False:
            app.logger.error('invalid JSON values')
            return Response("invalid values")
        #check if room_id is valid
        req_url = f"http://{os.getenv('ASSETS_API_HOST')}:{os.getenv('ASSETS_API_PORT')}/assets/rooms/"+content['room_id']+"/"
        #don't know why response for invalid uuid`s is a connectionError instead of Code 404, so workaraound was implemented
        try:
            response = requests.get(req_url)
        except requests.exceptions.ConnectionError:
            app.logger.error('invalid room_id')
            return Response("invalid room_id", status=422)
        
        #ckeck for conflicts with other reservations
        res_query = db.session.query(reservations).filter(reservations.room_id == content['room_id']).all()
        if res_query is not None:
            content_from = datetime.datetime.strptime(content.get('from'), '%Y-%m-%d')
            content_from = content_from.date()
            content_to = datetime.datetime.strptime(content.get('to'), '%Y-%m-%d')
            content_to = content_to.date()
            for entry in res_query:
                if ((content_from <= entry.from_date and content_to >= entry.from_date) or (content_from <= entry.to_date and content_to >= entry.to_date) or (content_from >= entry.from_date and content_to <= entry.to_date)):
                    app.logger.error('Conflict with other reservation')
                    return Response("conflicts with other reservations on the same room", status=409)
                
        #check if id key is present and add reservation
        if content.get('id') is not None:
            db.session.add(reservations(reservation_id = content['id'], from_date = content['from'], to_date = content['to'], room_id = content['room_id']))
        else:
            db.session.add(reservations(from_date = content['from'], to_date = content['to'], room_id = content['room_id']))
        #commit
        db.session.commit()
        #create response
        app.logger.info('Reservation was created')
        method_response = Response("reservation created", status=201)
        
    #GET Request
    if request.method == 'GET':
        app.logger.info('GET Function called')
        #validate values
        if checkQueryValues(request.args.get('before'), request.args.get('after'), request.args.get('room_id')) is False:
            app.logger.info('invalid query values')
            return Response("invalid query values")
        #make query, filter by parameters if present
        res_query = db.session.query(reservations)
        if request.args.get('room_id') is not None:
            res_query = res_query.filter(reservations.room_id == request.args.get('room_id'))  
        if request.args.get('before') is not None:
            res_query = res_query.filter(reservations.from_date < request.args.get('before'))
        if request.args.get('after') is not None:
            res_query = res_query.filter(reservations.to_date > request.args.get('after'))
        app.logger.info('Filter added')
        res_query.all()
        app.logger.info('Query done')
        #check if a reservation for the query is present
        if res_query is None:
            #create error response
            app.logger.error('Reservation was not found')
            method_response = Response("reservation not found", status=404)
        else:
            #convert query data to json object
            app.logger.error('Create Dictionary from result')
            data = []
            for entry in res_query:
                new_data = {"id":str(entry.reservation_id),
                            "from":str(entry.from_date),
                            "to":str(entry.to_date),
                            "room_id":str(entry.room_id)
                            }
                data.append(new_data)
            query_result_json = json.dumps(data)
            app.logger.error('dictionary converted to JSON')
            #create response with query values
            method_response = Response(query_result_json, status=200, mimetype='application/json')

    return method_response
        
        
@app.route("/reservations/<input_id>/", methods=['GET', 'PUT', 'DELETE'])
def reservations_byID(input_id: str): 
    app.logger.info('By ID Function Calles')
    #validate id
    try:
        uuid.UUID(input_id)
    except ValueError:
        app.logger.error('Invalid Id')
        return Response("invalid id", status=400)
    #make query for id
    app.logger.info('Make Query')
    #res_query = reservations.query.filter_by(reservation_id=input_id).first()
    #res_query = db.session.query(reservations)
    #res_query = res_query.filter(reservations.reservation_id == input_id)
    #res_query.first()
    res_query = db.session.query(reservations).filter(reservations.reservation_id == input_id).first()
    app.logger.info('Query done')

    #GET request
    if request.method == 'GET':
        app.logger.info('GET Request called')
        if res_query is None:
            app.logger.error('Reservation not found')
            method_response = Response("reservation not found", status=404)
        else:
            #convert query data to json object
            app.logger.info('Create Data Dictionary')
            app.logger.info(res_query)
            data ={}
            #data['id'] = str(res_query.reservation_id)
            data['from'] = str(res_query.from_date)
            data['to'] = str(res_query.to_date)
            data['room_id'] = str(res_query.room_id)
            app.logger.info('Dictionary Created')
            query_result_json = json.dumps(data)
            app.logger.info('Converted to JSON')
            #create response with query values
            method_response = Response(query_result_json, status=200, mimetype='application/json')

    #PUT request
    elif request.method == 'PUT':
        #get Values from Message Body
        content = request.json
        #validate JSON-Content values
        if checkJSONValues(content) is False:
            app.logger.error('Invalid parameters in JSON')
            return Response("invalid parameters in JSON Body", status=405)
        #check if room_id is valid
        req_url = "http://backend-assets:9000/assets/rooms/"+content['room_id']+"/"
        #don't know why response for invalid uuid`s is a connectionError instead of Code 404, so workaraound was implemented
        try:
            response = requests.get(req_url)
        except requests.exceptions.ConnectionError:
            app.logger.error('Invalid room_id')
            return Response("invalid room_id", status=422)
        
        #ckeck for conflicts with other reservations
        res_query_rooms = db.session.query(reservations).filter(reservations.room_id == content['room_id']).all()
        if res_query_rooms is not None:
            content_from = datetime.datetime.strptime(content.get('from'), '%Y-%m-%d')
            content_from = content_from.date()
            content_to = datetime.datetime.strptime(content.get('to'), '%Y-%m-%d')
            content_to = content_to.date()
            for entry in res_query_rooms:
                if ((content_from <= entry.from_date and content_to >= entry.from_date) or (content_from <= entry.to_date and content_to >= entry.to_date) or (content_from >= entry.from_date and content_to <= entry.to_date)):
                    app.logger.error('Conflicts with other Reservation')
                    return Response("conflicts with other reservations on the same room", status=409)
        
        if res_query is None:
            #insert new entry
            db.session.add(reservations(reservation_id = input_id, from_date = content['from'], to_date = content['to'], room_id = content['room_id']))     
        else:
            auth_header = request.headers.get('Authorization')
            if auth_header:
                auth_token = auth_header.split(" ")[1]
            else:
                auth_token = None
            #validate token
            resp = validate_jwt(auth_token)
            if resp is not True:
                return resp
            #update existing entry
            reservations.query.filter_by(reservation_id=input_id).update(dict(from_date=content['from'], to_date = content['to'], room_id = content['room_id']))
        #return response
        app.logger.info('Created/ Updated Reservation')
        method_response = Response("reservation created/updated", status=204) 
        
    #DELETE request
    else:
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = None
        #validate token
        resp = validate_jwt(auth_token)
        if resp is not True:
            return resp
        num_deleted = reservations.query.filter_by(reservation_id=input_id).delete()
        #check if object was deleted
        if num_deleted > 0 :
            app.logger.info('Reservation was deleted')
            method_response = Response("reservation deleted", status=204) 
        else:
            app.logger.error('Reservation was not found')
            method_response = Response("reservation not found", status=404)

    #commit changes
    db.session.commit()
    #return individual response
    return method_response

if __name__ == '__main__':
    #import custom db scheme
    from database import reservations
    with app.app_context(): 
        db.create_all()
    #define the localhost ip and the port that is going to be used
    app.run(host=os.getenv('HOST'), port=os.getenv('PORT'), debug=True)