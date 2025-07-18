from flask import Flask, request, jsonify, send_file, abort
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)



@app.route('/api/motd', methods=['GET'])
def get_motd():
    f = open("motd.txt","r")
    return jsonify(f.read().replace("\n",""))
    

app.run(debug=True,host="0.0.0.0",port=4000)
