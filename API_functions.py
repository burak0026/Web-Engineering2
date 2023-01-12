import json
from datetime import datetime
import requests
from flask import Response
from app import Flask_API
from validation import *
from authorization import *
from database import reservations

class API_functions:
    
    def reservations_status():
        
        Flask_API.app.logger.info('Get Statusinformation')
        return {
            "authors": "Burak Oezkan, Marius Engelmeier",
            "apiVersion": "1.0"
            }
    
    def post_reservations(request):
        # get auth token from header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = None
        #validate token
        resp = validate_jwt(auth_token,Flask_API.app)
        if resp is not True:
            return resp
        #get Values from Message Body
        content = request.json
        #validate JSON-Content values
        if checkJSONValues(content,Flask_API.app) is False:
            Flask_API.app.logger.error('invalid JSON values')
            return Response("invalid values")
        #check if room_id is valid
        req_url = f"http://{os.getenv('ASSETS_API_HOST')}:{os.getenv('ASSETS_API_PORT')}/assets/rooms/"+content['room_id']+"/"
        #don't know why response for invalid uuid`s is a connectionError instead of Code 404, so workaraound was implemented
        try:
            response = requests.get(req_url)
        except requests.exceptions.ConnectionError:
            Flask_API.app.logger.error('invalid room_id')
            return Response("invalid room_id", status=422)
        
        #ckeck for conflicts with other reservations
        res_query = Flask_API.db.session.query(reservations).filter(reservations.room_id == content['room_id']).all()
        if res_query is not None:
            content_from = datetime.datetime.strptime(content.get('from'), '%Y-%m-%d')
            content_from = content_from.date()
            content_to = datetime.datetime.strptime(content.get('to'), '%Y-%m-%d')
            content_to = content_to.date()
            for entry in res_query:
                if ((content_from <= entry.from_date and content_to >= entry.from_date) or (content_from <= entry.to_date and content_to >= entry.to_date) or (content_from >= entry.from_date and content_to <= entry.to_date)):
                    Flask_API.app.logger.error('Conflict with other reservation')
                    return Response("conflicts with other reservations on the same room", status=409)
                
        #check if id key is present and add reservation
        if content.get('id') is not None:
            Flask_API.db.session.add(reservations(reservation_id = content['id'], from_date = content['from'], to_date = content['to'], room_id = content['room_id']))
        else:
            Flask_API.db.session.add(reservations(from_date = content['from'], to_date = content['to'], room_id = content['room_id']))
        #commit
        Flask_API.db.session.commit()
        #create response
        Flask_API.app.logger.info('Reservation was created')
        return Response("reservation created", status=201)
    
    def get_reservations(request):
        #validate values
        if checkQueryValues(request.args.get('before'), request.args.get('after'), request.args.get('room_id'),Flask_API.app) is False:
            Flask_API.app.logger.error('invalid query values')
            return Response("invalid query values")
        #make query, filter by parameters if present
        res_query = Flask_API.db.session.query(reservations)
        if request.args.get('room_id') is not None:
            res_query = res_query.filter(reservations.room_id == request.args.get('room_id'))  
        if request.args.get('before') is not None:
            res_query = res_query.filter(reservations.from_date < request.args.get('before'))
        if request.args.get('after') is not None:
            res_query = res_query.filter(reservations.to_date > request.args.get('after'))
        res_query.all()
        #check if a reservation for the query is present
        if res_query is None:
            #create error response
            Flask_API.app.logger.error('Reservation was not found')
            return Response("reservation not found", status=404)
        else:
            #convert query data to json object
            data = []
            for entry in res_query:
                new_data = {"id":str(entry.reservation_id),
                            "from":str(entry.from_date),
                            "to":str(entry.to_date),
                            "room_id":str(entry.room_id)
                            }
                data.append(new_data)
            query_result_json = json.dumps(data)
            #create response with query values
            Flask_API.app.logger.info('Getting all reservations')
            return Response(query_result_json, status=200, mimetype='application/json')
    
    def get_reservation_by_id(input_id):
        
        if validate_id(input_id) is False:
            Flask_API.app.logger.error('Invalid Id')
            return Response("invalid id", status=400)

        #make query for id
        res_query = Flask_API.db.session.query(reservations).filter(reservations.reservation_id == input_id).first()
        
        #GET request

        if res_query is None:
            Flask_API.app.logger.error('Reservation not found')
            return Response("reservation not found", status=404)
        else:
            #convert query data to json object
            data ={}
            data['id'] = str(res_query.reservation_id)
            data['from'] = str(res_query.from_date)
            data['to'] = str(res_query.to_date)
            data['room_id'] = str(res_query.room_id)
            query_result_json = json.dumps(data)
            #create response with query values
            Flask_API.app.logger.info('Reservation was found')
            return Response(query_result_json, status=200, mimetype='application/json')
        
    def put_reservation_by_id(input_id,request):
        if validate_id(input_id) is False:
            Flask_API.app.logger.error('Invalid Id')
            return Response("invalid id", status=400)

        #make query for id
        res_query = Flask_API.db.session.query(reservations).filter(reservations.reservation_id == input_id).first()
        #get Values from Message Body
        content = request.json
        #validate JSON-Content values
        if checkJSONValues(content,Flask_API.app) is False:
            Flask_API.app.logger.error('Invalid parameters in JSON Body')
            return Response("invalid parameters in JSON Body", status=405)
        #check if room_id is valid
        req_url = "http://backend-assets:9000/assets/rooms/"+content['room_id']+"/"
        #don't know why response for invalid uuid`s is a connectionError instead of Code 404, so workaraound was implemented
        try:
            response = requests.get(req_url)
        except requests.exceptions.ConnectionError:
            Flask_API.app.logger.error('Invalid room_id')
            return Response("invalid room_id", status=422)
        
        #ckeck for conflicts with other reservations
        res_query_rooms = Flask_API.db.session.query(reservations).filter(reservations.room_id == content['room_id']).all()
        if res_query_rooms is not None:
            content_from = datetime.datetime.strptime(content.get('from'), '%Y-%m-%d')
            content_from = content_from.date()
            content_to = datetime.datetime.strptime(content.get('to'), '%Y-%m-%d')
            content_to = content_to.date()
            for entry in res_query_rooms:
                if ((content_from <= entry.from_date and content_to >= entry.from_date) or (content_from <= entry.to_date and content_to >= entry.to_date) or (content_from >= entry.from_date and content_to <= entry.to_date)):
                    Flask_API.app.logger.error('conflict with other reservation on the same room')
                    return Response("conflict with other reservation on the same room", status=409)
        if res_query is None:
            #insert new entry
            Flask_API.app.logger.info('add new entry')
            Flask_API.db.session.add(reservations(reservation_id = input_id, from_date = content['from'], to_date = content['to'], room_id = content['room_id']))     
        else:
            Flask_API.app.logger.info('update entry')
            auth_header = request.headers.get('Authorization')
            if auth_header:
                auth_token = auth_header.split(" ")[1]
            else:
                auth_token = None
            #validate token
            resp = validate_jwt(auth_token,Flask_API.app)
            if resp is not True:
                return resp
            #update existing entry
            if content['from'] is not None:
                res_query.from_date = content['from']
            if content['to'] is not None:    
                res_query.to_date = content['to']
            if content['room_id'] is not None:
                res_query.room_id = content['room_id']

        #commit changes
        Flask_API.db.session.commit()
        #return response
        Flask_API.app.logger.info('Reservation was created/updated')
        return Response("reservation created/updated", status=204)
    
    def delete_reservation_by_id(input_id,request):
        
        if validate_id(input_id) is False:
            Flask_API.app.logger.error('Invalid Id')
            return Response("invalid id", status=400)

        #make query for id
        res_query = Flask_API.db.session.query(reservations).filter(reservations.reservation_id == input_id).first()
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = None
        #validate token
        resp = validate_jwt(auth_token,Flask_API.app)
        if resp is not True:
            return resp
        #num_deleted = res_query.delete()
        if res_query is None:
            Flask_API.app.logger.error('Reservation was not found')
            return Response("reservation not found", status=404)
        else:
            Flask_API.db.session.delete(res_query)
            #commit changes
            Flask_API.db.session.commit()
            Flask_API.app.logger.info("Reservation was deleted")
            return Response("reservation deleted", status=204)
    
    