import os
import pgdb
import datetime
import uuid
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

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
    #open DB Connection and get cursor
    #conn = pgdb.connect(host="postgres", port = 5432, database="reservations", user="postgres", password="postgres")
    conn = pgdb.connect(host=os.getenv('POSTGRES_RESERVATIONS_HOST'), port=os.getenv('POSTGRES_RESERVATIONS_PORT'), database=os.getenv('POSTGRES_RESERVATIONS_DBNAME'), user=os.getenv('POSTGRES_RESERVATIONS_USER'), password=os.getenv('POSTGRES_RESERVATIONS_PASSWORD'))
    cur = conn.cursor()
    #POST Request
    if request.method == 'POST':
        #get Values from Message Body
        content = request.json
        #initialize variables
        sqlStatement = ''
        param_id = ""
        input_id = ""
        input_from = content['from']
        input_to = content['to']
        input_room_id = content['room_id']
        #check if id key is present, set values to modify string
        if content.get('id') is not None:
            param_id = "id, "
            input_id = content['id']
            #validate id
            try:
                uuid.UUID(str(input_id))
                input_id = input_id + "', '"
            except ValueError:
                return jsonify(response='invalid id uuid')
        #validate FROM
        try:
            datetime.datetime.strptime(input_from, '%Y-%m-%d')
        except ValueError:
            return jsonify(response='invalid from Date')
        #validate TO
        try:
            datetime.datetime.strptime(input_to, '%Y-%m-%d')
        except ValueError:
            return jsonify(response='invalid to Date')
        #validate room_id
        try:
            uuid.UUID(str(input_room_id))
        except ValueError:
            return jsonify(response='invalid room_id uuid')
        #create SQL statement
        sqlStatement = "INSERT INTO reservations ("+ param_id +"\"from\", \"to\", room_id) VALUES ('"+ input_id +""+ input_from +"', '"+ input_to +"', '"+ input_room_id +"')"
        #execute SQL-Statement, make new Database entry
        cur.execute(sqlStatement)
        #close cursor, commit the SQL-Statement and close DB onnection
        cur.close()
        conn.commit()
        conn.close()  
        #return
        return Response(status=201, mimetype='application/json')
    
    #GET Request
    else:
        cur.execute("SELECT * FROM reservations")
        query_results = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(query_results)
    
        
@app.route("/reservations/<string>", methods=['GET'])
def reservations_byID(string: str): 
    return jsonify(
        response=string
    )


if __name__ == '__main__':
    #define the localhost ip and the port that is going to be used
    app.run(host='0.0.0.0', port=os.getenv('PORT'))