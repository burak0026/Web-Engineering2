from app import App
from routing_functions import Routing_functions
from flask import request
import uuid
import os

@App.app.route("/reservations/status/", methods=['GET'])
def status():
    return Routing_functions.reservations_status()

@App.app.route("/reservations/", methods=['GET', 'POST'])
def reservations():
    
    if request.method == 'GET':
        return Routing_functions.get_reservations(request)
    
    if request.method == 'POST':
        return Routing_functions.post_reservations(request)
    
@App.app.route("/reservations/<input_id>/", methods=['GET', 'PUT', 'DELETE'])
def reservation_by_id(id: uuid):
    
    if request.method == 'GET':
        
        return Routing_functions.get_reservation_by_id(id)
        
    elif request.method == 'PUT':
        
        return Routing_functions.put_reservation_by_id(id,request)
    
    elif request.method == 'DELETE':
        
        return Routing_functions.delete_reservation_by_id(id,request)


if __name__ == '__main__':
    #define the localhost ip and the port that is going to be used
    App.app.run(host=os.getenv('HOST'), port=os.getenv('PORT'), debug=True)