import json
from datetime import datetime
import uuid
import requests
from flask import jsonify, Response
from sqlalchemy.dialects.postgresql import UUID
from app import App,reservations
from api_functions import checkQueryValues,checkJSONValues
from authorization import *


class Routing_functions():
    
    def reservations_status():
        App.app.logger.info('Get Statusinformation')
        return {
            "authors": "Burak Oezkan, Marius Engelmeier",
            "apiVersion": "1.0"
            }
    
    def post_reservations(request):
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
            App.app.logger.error('invalid JSON values')
            return Response("invalid values")
        #check if room_id is valid
        req_url = f"http://{os.getenv('ASSETS_API_HOST')}:{os.getenv('ASSETS_API_PORT')}/assets/rooms/"+content['room_id']+"/"
        #don't know why response for invalid uuid`s is a connectionError instead of Code 404, so workaraound was implemented
        try:
            response = requests.get(req_url)
        except requests.exceptions.ConnectionError:
            App.app.logger.error('invalid room_id')
            return Response("invalid room_id", status=422)
        
        #ckeck for conflicts with other reservations
        res_query = App.db.session.query(reservations).filter(reservations.room_id == content['room_id']).all()
        if res_query is not None:
            content_from = datetime.datetime.strptime(content.get('from'), '%Y-%m-%d')
            content_from = content_from.date()
            content_to = datetime.datetime.strptime(content.get('to'), '%Y-%m-%d')
            content_to = content_to.date()
            for entry in res_query:
                if ((content_from <= entry.from_date and content_to >= entry.from_date) or (content_from <= entry.to_date and content_to >= entry.to_date) or (content_from >= entry.from_date and content_to <= entry.to_date)):
                    App.app.logger.error('Conflict with other reservation')
                    return Response("conflicts with other reservations on the same room", status=409)
                
        #check if id key is present and add reservation
        if content.get('id') is not None:
            App.db.session.add(reservations(reservation_id = content['id'], from_date = content['from'], to_date = content['to'], room_id = content['room_id']))
        else:
            App.db.session.add(reservations(from_date = content['from'], to_date = content['to'], room_id = content['room_id']))
        #commit
        App.db.session.commit()
        #create response
        App.app.logger.info('Reservation was created')
        return Response("reservation created", status=201)

    def get_reservations(request):
        #validate values
        if checkQueryValues(request.args.get('before'), request.args.get('after'), request.args.get('room_id')) is False:
            App.app.logger.info('Reservation was created')
            return Response("reservation created")
        #make query, filter by parameters if present
        res_query = App.db.session.query(reservations)
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
            App.app.logger.error('Reservation was not found')
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
            return Response(query_result_json, status=200, mimetype='application/json')
    
    def get_reservation_by_id(input_id: str):
         #validate id
        try:
            uuid.UUID(input_id)
        except ValueError:
            App.app.logger.error('Invalid Id')
            return Response("invalid id", status=400)
        #make query for id
        res_query = reservations.query.filter_by(reservation_id=input_id).first()
        
        if res_query is None:
            App.app.logger.error('Reservation not found')
            return Response("reservation not found", status=404)
        else:
            #convert query data to json object
            data ={}
            data['id'] = str(res_query.reservation_id)
            data['from'] = str(res_query.from_date)
            data['to'] = str(res_query.to_date)
            data['room_id'] = str(res_query.room_id)
            query_result_json = json.dumps(data)
            App.db.session.commit()
            #create response with query values
            return Response(query_result_json, status=200, mimetype='application/json')
        
    def put_reservation_by_id(input_id: str,request):
            #validate id
        try:
            uuid.UUID(input_id)
        except ValueError:
            App.app.logger.error('Invalid Id')
            return Response("invalid id", status=400)
        #make query for id
        res_query = reservations.query.filter_by(reservation_id=input_id).first()
        #get Values from Message Body
        content = request.json
        #validate JSON-Content values
        if checkJSONValues(content) is False:
            App.app.logger.error('Invalid parameters in JSON')
            return Response("invalid parameters in JSON Body", status=405)
        #check if room_id is valid
        req_url = "http://backend-assets:9000/assets/rooms/"+content['room_id']+"/"
        #don't know why response for invalid uuid`s is a connectionError instead of Code 404, so workaraound was implemented
        try:
            response = requests.get(req_url)
        except requests.exceptions.ConnectionError:
            App.app.logger.error('Invalid room_id')
            return Response("invalid room_id", status=422)
        
        #ckeck for conflicts with other reservations
        res_query_rooms = App.db.session.query(reservations).filter(reservations.room_id == content['room_id']).all()
        if res_query_rooms is not None:
            content_from = datetime.datetime.strptime(content.get('from'), '%Y-%m-%d')
            content_from = content_from.date()
            content_to = datetime.datetime.strptime(content.get('to'), '%Y-%m-%d')
            content_to = content_to.date()
            for entry in res_query_rooms:
                if ((content_from <= entry.from_date and content_to >= entry.from_date) or (content_from <= entry.to_date and content_to >= entry.to_date) or (content_from >= entry.from_date and content_to <= entry.to_date)):
                    App.app.logger.error('Conflicts with other Reservation')
                    return Response("conflicts with other reservations on the same room", status=409)
        
        if res_query is None:
            #insert new entry
            App.db.session.add(reservations(reservation_id = input_id, from_date = content['from'], to_date = content['to'], room_id = content['room_id']))     
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
        App.app.logger.info('Created/ Updated Reservation')
        App.db.session.commit()
        return Response("reservation created/updated", status=204)
    
    def delete_reservation_by_id(input_id: str,request):
        #validate id
        try:
            uuid.UUID(input_id)
        except ValueError:
            App.app.logger.error('Invalid Id')
            return Response("invalid id", status=400)
        #make query for id
        res_query = reservations.query.filter_by(reservation_id=input_id).first()
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
            App.app.logger.info('Reservation was deleted')
            App.db.session.commit()
            return Response("reservation deleted", status=204) 
        else:
            App.app.logger.error('Reservation was not found')
            App.db.session.commit()
            return Response("reservation not found", status=404)
