from flask import Flask, jsonify, request
from flask_cors import CORS

import uuid
import os
from dotenv import load_dotenv

from lib.response import resp

load_dotenv()
app = Flask(__name__)
CORS(app) #resources=...

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/api/create-user', methods=['POST'])
def create_user():
    try:
        return jsonify(resp(True, "Successfully created user", {

        })), 201
    except Exception as err:
        print(err)
        return jsonify(resp(False, "There was an error while trying to create user")), 500 #? can I not return an error?