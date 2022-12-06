import os
import json
import datetime
import uuid
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
    #validate FROM
    if content.get('from') is not None:
        try:
            datetime.datetime.strptime(content['from'], '%Y-%m-%d')
        except ValueError:
            return False
    #validate TO
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

#Defining the Routes

@app.route('/')
def welcome():
    # return a json
    return jsonify({'status': 'api working'})


@app.route("/reservations/status", methods=['GET'])
def reservations_status():
    return Response("{'message':'status ok'}", status=200, mimetype='application/json')


@app.route("/reservations/", methods=['GET', 'POST'])
def reservations_general():
    
    #POST Request
    if request.method == 'POST':
        #get Values from Message Body
        content = request.json
        #validate JSON-Content values
        if checkJSONValues(content) is False:
            return jsonify("invalid values")
        #check if id key is present
        if content.get('id') is not None:
            db.session.add(reservations(reservation_id = content['id'], from_date = content['from'], to_date = content['to'], room_id = content['room_id']))
        else:
            db.session.add(reservations(from_date = content['from'], to_date = content['to'], room_id = content['room_id']))
        #commit
        db.session.commit()
        #create response
        method_response = Response("reservation created", status=201, mimetype='application/json')
        
    #GET Request
    else:
        method_response = Response(status=202, mimetype='application/json')

    return method_response
        
        
@app.route("/reservations/<input_id>", methods=['GET', 'PUT', 'DELETE'])
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
    app.run(host='0.0.0.0', port=os.getenv('PORT'))