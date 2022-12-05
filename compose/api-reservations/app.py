import os
import pgdb
import json
import datetime
import uuid
from flask import Flask, jsonify, request, Response, make_response

app = Flask(__name__)

#load postgres parameter
pgdb_res_host = os.getenv('POSTGRES_RESERVATIONS_HOST')
pgdb_res_port = os.getenv('POSTGRES_RESERVATIONS_PORT')
pgdb_res_database = os.getenv('POSTGRES_RESERVATIONS_DBNAME')
pgdb_res_user = os.getenv('POSTGRES_RESERVATIONS_USER')
pgdb_res_password = os.getenv('POSTGRES_RESERVATIONS_PASSWORD')


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
    #open DB Connection and get cursor
    conn = pgdb.connect(host=pgdb_res_host, port=pgdb_res_port, database=pgdb_res_database, user=pgdb_res_user, password=pgdb_res_password)
    cur = conn.cursor()
    #POST Request
    if request.method == 'POST':
        #get Values from Message Body
        content = request.json
        #validate JSON-Content values
        if checkJSONValues(content) is False:
            return jsonify("invalid values")
        #initialize variables for special case id
        param_id = ''
        sql_id_value = ''
        #check if id key is present, set values to modify string
        if content.get('id') is not None:
            param_id = "id, "
            sql_id_value = content['id'] + "', '"       
        #create SQL statement
        sqlStatement = "INSERT INTO "+ pgdb_res_database +" ("+ param_id +"\"from\", \"to\", room_id) VALUES ('"+ sql_id_value +""+ content['from'] +"', '"+ content['to'] +"', '"+ content['room_id'] +"')"
        #execute SQL-Statement, make new Database entry
        cur.execute(sqlStatement)
        #create response
        method_response = Response(status=201, mimetype='application/json')
    
    #GET Request
    else:
        cur.execute("SELECT * FROM "+ pgdb_res_database +"")
        query_results = cur.fetchall()
        method_response = query_results

    #close cursor, commit the SQL-Statement and close DB onnection
    cur.close()
    conn.commit()
    conn.close() 
    #return response
    return method_response
        
@app.route("/reservations/<input_id>", methods=['GET', 'PUT', 'DELETE'])
def reservations_byID(input_id: str): 
    #open DB Connection and get cursor
    conn = pgdb.connect(host=pgdb_res_host, port=pgdb_res_port, database=pgdb_res_database, user=pgdb_res_user, password=pgdb_res_password)
    cur = conn.cursor()
    #validate id
    try:
        uuid.UUID(input_id)
    except ValueError:
        return Response(status=400, mimetype='application/json')
        
    #GET request
    if request.method == 'GET':
        #create sql statement
        sqlStatement = "SELECT * FROM "+ pgdb_res_database +" WHERE id = '"+ input_id +"'"
        #execute SQL-Statement, save query result
        cur.execute(sqlStatement)
        query_result = cur.fetchall()
        #check if a reservation was found, exception if not
        if cur.rowcount == 0:
            method_response = Response(status=404, mimetype='application/json')
        else:
            #convert data to json object
            data ={}
            for i in range(len(cur.description)):
                data[cur.description[i][0]] = str(query_result[0][i])
            query_results_json = json.dumps(data)
            #create response with query values
            method_response = Response(query_results_json, status=200, mimetype='application/json')
    
    #PUT request
    elif request.method == 'PUT':
        #get Values from Message Body
        content = request.json
        #validate JSON-Content values
        if checkJSONValues(content) is False:
            return jsonify("invalid values")
        #check if id already in use
        sqlStatement = "SELECT * FROM "+ pgdb_res_database +" WHERE id = '"+ input_id +"'"
        cur.execute(sqlStatement)
        if cur.rowcount == 0:
            #create SQL statement
            sqlStatement = "INSERT INTO "+ pgdb_res_database +" (id, \"from\", \"to\", room_id) VALUES ('"+ input_id +"', '"+ content['from'] +"', '"+ content['to'] +"', '"+ content['room_id'] +"')"
            #execute SQL-Statement to make new Database entry, commit change
            cur.execute(sqlStatement)
            method_response = Response(status=204, mimetype='application/json')
        else:
            #create SQL statement
            sqlStatement = "UPDATE "+ pgdb_res_database +" SET \"from\" =  '"+ content['from'] +"', \"to\" = '"+ content['to'] +"', room_id = '"+ content['room_id'] +"' WHERE id = '"+ input_id +"'"
            #execute SQL-Statement to make new Database entry, commit change
            cur.execute(sqlStatement)
            method_response = Response(status=204, mimetype='application/json')

    #DELETE request
    else:
        #create sql statement
        sqlStatement = "DELETE FROM "+ pgdb_res_database +" WHERE id = '"+ input_id +"'"
        #execute SQL-Statement
        cur.execute(sqlStatement)
        #if no entry was found: throw exception
        if cur.rowcount == 0:
            method_response = Response(status=404, mimetype='application/json')
        else:
            #create response
            method_response = Response(status=200, mimetype='application/json')

    #close cursor, commit and close DB onnection
    cur.close()
    conn.commit()
    conn.close()
    #return individual response
    return method_response

if __name__ == '__main__':
    #define the localhost ip and the port that is going to be used
    app.run(host='0.0.0.0', port=os.getenv('PORT'))