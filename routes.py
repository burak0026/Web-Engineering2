from app import Flask_API
from API_functions import API_functions
from flask import request
import os
import uuid

app=Flask_API.app

#Defining the Routes
@app.route("/reservations/status/", methods=['GET'])
def reservation_status():
    
    return API_functions.reservations_status()


@app.route("/reservations/", methods=['GET', 'POST'])
def reservations():
    
    if request.method == 'GET':
        return API_functions.get_reservations(request)
    elif request.method == 'POST':
        return API_functions.post_reservations(request)

@app.route("/reservations/<input_id>/", methods=['GET', 'PUT', 'DELETE'])
def reservation_by_id(input_id: str):
    
    if request.method == 'GET':
        return API_functions.get_reservation_by_id(input_id)
    elif request.method == 'PUT':
        return API_functions.put_reservation_by_id(input_id,request)
    elif request.method == 'DELETE':
        return API_functions.delete_reservation_by_id(input_id,request)
    
if __name__ == '__main__':
    #import custom db scheme
    # from database import reservations
    # with app.app_context(): 
    #     db.create_all()
    #define the localhost ip and the port that is going to be used
    app.run(host=os.getenv('HOST'), port=os.getenv('PORT'), debug=True)