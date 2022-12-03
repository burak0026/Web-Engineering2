import os
import pgdb
from flask import Flask, jsonify, request

app = Flask(__name__)

#Defining the Routes

@app.route('/')
def welcome():
    # return a json
    return jsonify({'status': 'api working'})


@app.route("/reservations/status", methods=['GET'])
def reservations_status():
    return jsonify(
        response="*statuscode*"
    )


@app.route("/reservations/", methods=['GET', 'POST'])
def reservations_general():
    #open DB Connection and get cursor
    conn = pgdb.connect(host="postgres", port = 5432, database="reservations", user="postgres", password="postgres")
    cur = conn.cursor()
    #POST Request
    if request.method == 'POST':
        #get Values from Message Body
        content = request.json
        #initialize variables
        sqlStatement = ''
        #input_id = content['id']
        input_from = content['from']
        input_to = content['to']
        input_room_id = content['room_id']
        #validate inputs
        #-------implement------------
        #create SQL statement
        sqlStatement = "INSERT INTO reservations (\"from\", \"to\", room_id) VALUES ('"+ input_from +"', '"+ input_to +"', '"+ input_room_id +"')"
        #execute SQL-Statement, make new Database entry
        cur.execute(sqlStatement)
        #close cursor, commit the SQL-Statement and close DB onnection
        cur.close()
        conn.commit()
        conn.close()  
        #return ok
        return jsonify(
            response='ok'
        )
    
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