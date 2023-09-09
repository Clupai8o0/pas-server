from flask import Flask, jsonify, request
from flask_cors import CORS

import uuid

from dotenv import load_dotenv
import os
import jwt
import datetime

from lib.encrypter import encrypt, decrypt, generateKey, hashPw, checkPw
from lib.response import resp, verifySession

from db.index import createUser, createPassword, getPasswords

load_dotenv()
app = Flask(__name__)
CORS()
# CORS(app, resources={r"*": {"origins": "http://localhost:3000"}})

@app.route('/')
def home():
  return 'Hello, World!'

@app.route('/test-1')
def test1():
  try:
    token = jwt.encode({
      "user": 123,
      "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=3)
    }, os.getenv('SECRET'), algorithm="HS256")
    return jsonify(resp(True, "Ok here u go", {
      "session": token,
      "secret": os.getenv('SECRET')
    }))
  except Exception as err:
    print(err)
    return jsonify(resp(False, "Could not lol", str(err)))

@app.route('/test-2')
def test2():
  try:
    session = request.json['session']
    valid, obj = verifySession(session)
    return jsonify(resp(True, "Ok here u go", {
      "valid": valid,
      "obj": obj
    }))
  except Exception as err:
    print(err)
    return jsonify(resp(False, "Could not lol", str(err)))

# Create User
@app.route("/api/create-user", methods=['POST'])
def create_user():
  try:
    # Properties - email, username, password
    ip = request.json['ip']
    email = request.json['email']
    username = request.json['username']
    password = request.json['password']
    
    hash = hashPw(password)
    key = generateKey()
    userId = uuid.uuid4()
    
    # add user to database
    session = createUser(userId, ip, username, email, password, hash, key)

    # add login to database

    #todo add to login as well

    # todo this will be saved on local storage
    return jsonify(resp(True, "Successfully created user", {
      "session": f"{session}"
    }))
  except Exception as err:
    print(err)
    return jsonify(resp(False, "There was an error while trying to create user"), str(err)), 500

# Login
@app.route("/api/login", methods=['POST'])
def login():
  return jsonify({ "success": True })

# Add/Delete/Update/Get/Search  Password
@app.route("/api/create-password", methods=['POST'])
def create_password():
  try:
    title = request.json['title']
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    url = request.json['url']
    session = request.json['session']

    valid, obj = verifySession(session)
    # todo: hash the password using hash key

    if valid:
      createPassword(obj['id'], title, url, username, email, password)
    else:
      raise Exception("expired") # todo: need to make this more obv with better HTTP

    return jsonify(resp(True, "Successfully created password")), 201
  except Exception as err:
    print(err)
    return jsonify(resp(False, "There was an error while trying to create password", str(err))), 500

@app.route("/api/get-passwords", methods=['GET'])
def get_passwords():
  try:
    session = request.json['session'] # todo: use auth headers for this

    valid, obj = verifySession(session)

    if valid:
      return jsonify(resp(True, "Successfully GET passwords of user", getPasswords(obj)[1]))
    else: 
      raise Exception('expired')
  except Exception as err:
    print(err)
    return jsonify(resp(False, "There was an error while trying to get passwords", str(err))), 500

@app.route("/api/delete-password", methods=['DELETE'])
def deletePassword():
  return jsonify({ "success": True })

@app.route("/api/update-password", methods=['PUT'])
def updatePassword():
  return jsonify({ "success": True })

@app.route("/api/search-passwords", methods=['GET'])
def searchPasswords():
  print(request.args['query']) 
  return jsonify({ "success": True })

# @app.route('/convert/<string:fromType>/<string:toType>/<string:value>', methods=['GET'])
# def convert(fromType, toType, value):
#   response = jsonify({})
#   response.headers.add("Access-Control-Allow-Origin", "*")  
#   return response