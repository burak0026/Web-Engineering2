import os
import json
import datetime
import uuid
import requests
import jwt
from flask import Flask, jsonify, request, Response, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID


#create flask app and configure
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://'+os.getenv('POSTGRES_RESERVATIONS_USER')+':'+os.getenv('POSTGRES_RESERVATIONS_PASSWORD')+'@'+os.getenv('POSTGRES_RESERVATIONS_HOST')+':'+os.getenv('POSTGRES_RESERVATIONS_PORT')+'/'+os.getenv('POSTGRES_RESERVATIONS_DBNAME')+''
db = SQLAlchemy(app)

#create model class with database scheme
class reservations(db.Model):
    reservation_id = db.Column("id", UUID(as_uuid=True), primary_key = True, default=uuid.uuid4)
    from_date = db.Column("from", db.String(50))
    to_date = db.Column("to", db.String(50))  
    room_id = db.Column("room_id", UUID(as_uuid=True), default=uuid.uuid4)

#init class to map parameters to 
def __init__(self, reservation_id, from_date, to_date, room_id):
    self.reservation_id = reservation_id
    self.from_date = from_date
    self.to_date = to_date
    self.room_id = room_id

#create the database connector
with app.app_context():
    db.create_all()

#function to check JSON parameters
def checkJSONValues(content):
    #validate id
    if content.get('id') is not None:  
        try:
            uuid.UUID(str(content['id']))
        except ValueError:
            return False
    #validate from
    if content.get('from') is not None:
        try:
            datetime.datetime.strptime(content['from'], '%Y-%m-%d')
        except ValueError:
            return False
    #validate to
    if content.get('to') is not None:
        try:
            datetime.datetime.strptime(content['to'], '%Y-%m-%d')
        except ValueError:
            return False
    #validate room_id
    if content.get('room_id') is not None:
        try:
            uuid.UUID(str(content['room_id']))
        except ValueError:
            return False
    #if no error, return true
    return True

#function to check JSON parameters
def checkQueryValues(before, after, room_id):
    #validate before
    if before is not None:
        try:
            datetime.datetime.strptime(before, '%Y-%m-%d')
        except ValueError:
            return False
    #validate after
    if after is not None:
        try:
            datetime.datetime.strptime(after, '%Y-%m-%d')
        except ValueError:
            return False
    #validate room_id
    if room_id is not None:
        try:
            uuid.UUID(str(room_id))
        except ValueError:
            return False
    #if no error, return true
    return True



def validate_jwt(token):
    if token is None:
        return Response("token not found", status=401)
    #get public key from Keycloak
    keycloak_url = f"http://{os.getenv('KEYCLOAK_HOST')}/auth/realms/{os.getenv('KEYCLOAK_REALM')}"
    keycloak_request = requests.get(keycloak_url)
    keycloak_request_json = json.loads(keycloak_request.text)
    keycloak_pubkey = keycloak_request_json["public_key"]
    #check if key is present, else throw 401
    if keycloak_pubkey is None:
        return Response("public key not found", status=401)
    #check if token is valid
    try:
        jwt.decode(token,keycloak_pubkey,algorithms=["RS256"])
        return Response("decode successfull", status=222)
    except Exception:
        return Response("decode failed", status=401)





#Defining the Routes

@app.route("/reservations/test/", methods=['GET'])
def reservations_test():
    pass


@app.route("/reservations/status/", methods=['GET'])
def reservations_status():

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
        validate_jwt(auth_token)
        #get Values from Message Body
        content = request.json
        #validate JSON-Content values
        if checkJSONValues(content) is False:
            return jsonify("invalid values")
        #check if room_id is valid
        req_url = "http://backend-assets:9000/assets/rooms/"+content['room_id']+"/"
        #don't know why response for invalid uuid`s is a connectionError instead of Code 404, so workaraound was implemented
        try:
            response = requests.get(req_url)
        except requests.exceptions.ConnectionError:
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
                    return Response("conflicts with other reservations on the same room", status=409, mimetype='application/json')
                
        #check if id key is present and add reservation
        if content.get('id') is not None:
            db.session.add(reservations(reservation_id = content['id'], from_date = content['from'], to_date = content['to'], room_id = content['room_id']))
        else:
            db.session.add(reservations(from_date = content['from'], to_date = content['to'], room_id = content['room_id']))
        #commit
        db.session.commit()
        #create response
        method_response = Response("reservation created", status=201, mimetype='application/json')
        
    #GET Request
    if request.method == 'GET':
        #validate values
        if checkQueryValues(request.args.get('before'), request.args.get('after'), request.args.get('room_id')) is False:
            return jsonify("invalid values")
        #make query, filter by parameters if present
        res_query = db.session.query(reservations)
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
            method_response = Response("reservation not found", status=404, mimetype='application/json')
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
            method_response = Response(query_result_json, status=200, mimetype='application/json')

    return method_response
        
        
@app.route("/reservations/<input_id>/", methods=['GET', 'PUT', 'DELETE'])
def reservations_byID(input_id: str): 
    #validate id
    try:
        uuid.UUID(input_id)
    except ValueError:
        return Response(status=400, mimetype='application/json')
    #make query for id
    res_query = reservations.query.filter_by(reservation_id=input_id).first()

    #GET request
    if request.method == 'GET':
        if res_query is None:
            method_response = Response("reservation not found", status=404, mimetype='application/json')
        else:
            #convert query data to json object
            data ={}
            data['id'] = str(res_query.reservation_id)
            data['from'] = str(res_query.from_date)
            data['to'] = str(res_query.to_date)
            data['room_id'] = str(res_query.room_id)
            query_result_json = json.dumps(data)
            #create response with query values
            method_response = Response(query_result_json, status=200, mimetype='application/json')

    #PUT request
    elif request.method == 'PUT':
        #get Values from Message Body
        content = request.json
        #validate JSON-Content values
        if checkJSONValues(content) is False:
            return Response("invalid parameters in JSON Body", status=405, mimetype='application/json')
        if res_query is None:
            #insert new entry
            db.session.add(reservations(reservation_id = input_id, from_date = content['from'], to_date = content['to'], room_id = content['room_id']))     
        else:
            #update existing entry
            reservations.query.filter_by(reservation_id=input_id).update(dict(from_date=content['from'], to_date = content['to'], room_id = content['room_id']))
        #return response
        method_response = Response("reservation created/updated", status=204, mimetype='application/json') 
        
    #DELETE request
    else:
        num_deleted = reservations.query.filter_by(reservation_id=input_id).delete()
        #check if object was deleted
        if num_deleted > 0 :
            method_response = Response("reservation deleted", status=204, mimetype='application/json') 
        else:
            method_response = Response("reservation not found", status=404, mimetype='application/json')

    #commit changes
    db.session.commit()
    #return individual response
    return method_response

if __name__ == '__main__':
    #define the localhost ip and the port that is going to be used
    app.run(host=os.getenv('HOST'), port=os.getenv('PORT'), debug=True)