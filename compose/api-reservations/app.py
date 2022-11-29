import os
from flask import Flask, jsonify, request

import pgdb



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
    if request.method == 'POST':
        content = request.json
        return jsonify(response=content['id'])
    else:
        conn = pgdb.connect(host="postgres", port = 5432, database="reservations", user="postgres", password="postgres")
        cur = conn.cursor()
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