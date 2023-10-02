from flask import Flask, jsonify, request
from flask_cors import CORS

import uuid

from dotenv import load_dotenv

from lib.encrypter import generateKey, hashPassword, encrypt
from lib.response import resp
from lib.session import verifySession

from db.index import createUser, createPassword, getPasswords, loginUser, deletePassword, updatePassword, searchPassword

load_dotenv()
app = Flask(__name__)
CORS()
# CORS(app, resources={r"*": {"origins": "http://localhost:3000"}})

@app.route('/')
def home():
  return 'Hello, World!'

#* Create User
@app.route("/api/create-user", methods=['POST'])
def create_user():
  try:
    body = request.json

    # ensuring all parameters are provided
    if not 'ip' in body:
      raise Exception("Missing ip parameter in body")
    if not 'email' in body:
      raise Exception("Missing email parameter in body")
    if not 'username' in body:
      raise Exception("Missing username parameter in body")
    if not 'password' in body:
      raise Exception("Missing password parameter in body")
    
    # generate hashes for security
    hashedPassword = hashPassword(body['password'])
    passwordKey = generateKey()
    userId = uuid.uuid4()
    
    # adding user to database
    createUser(userId, body['ip'], body['username'], body['email'], hashedPassword, passwordKey)
    session = loginUser(body['ip'], body['username'], body['password'])

    return jsonify(resp(True, "Successfully created user", session)) # todo: session format has been changed
  except Exception as err:
    print(err)
    return jsonify(resp(False, "There was an error while trying to create user", str(err))), 500

# Login
@app.route("/api/login", methods=['POST'])
def login():
  try:
    body = request.json

    # checking if parameters are given
    if not 'ip' in body:
      raise Exception("Missing parameter ip in body")
    if not 'username' in body:
      raise Exception("Missing parameter username in body")
    if not 'password' in body:
      raise Exception("Missing parameter password in body")

    session = loginUser(body['ip'], body['username'], body['password'])

    return jsonify(resp(True, "Successfully logged user", session))
  except Exception as err:
    print(err)
    return jsonify(resp(False, "There was an error while trying to login user", str(err))), 500

# Add/Delete/Update/Get/Search  Password
@app.route("/api/create-password", methods=['POST'])
def create_password():
  try:
    session = request.headers.get('authorization').split(' ')[1]
    if not session:
      raise Exception("Missing auth header authorization")

    body = request.json

    # checking if parameters are given
    if not 'title' in body:
      raise Exception("Missing parameter title in body")
    if not 'username' in body:
      raise Exception("Missing parameter username in body")
    if not 'email' in body:
      raise Exception("Missing parameter email in body")
    if not 'password' in body:
      raise Exception("Missing parameter password in body")
    if not 'url' in body:
      raise Exception("Missing parameter url in body")

    # verifying session & generated encrypted password
    valid, obj = verifySession(session)
    print(obj['key'])
    print(generateKey())
    encryptedPassword = encrypt(body['password'], obj['key'])

    if valid:
      createPassword(
        userId=obj['id'], 
        title=body['title'], 
        url=body['url'], 
        username=body['username'], 
        email=body['email'], 
        password=encryptedPassword
      )
    else:
      raise Exception("expired") # todo: expired has to be noticeable on frontend

    return jsonify(resp(True, "Successfully created password")), 201
  except Exception as err:
    print(err)
    return jsonify(resp(False, "There was an error while trying to create password", str(err))), 500

@app.route("/api/get-passwords", methods=['GET'])
def get_passwords():
  try:
    session = request.headers.get('authorization').split(' ')[1]

    if not session:
      raise Exception("Missing session parameter")

    valid, obj = verifySession(session)

    if valid:
      return jsonify(resp(True, "Successfully GET passwords of user", getPasswords(obj['id'])))
    else: 
      raise Exception("expired")
  except Exception as err:
    print(err)
    return jsonify(resp(False, "There was an error while trying to get passwords", str(err))), 500

@app.route("/api/delete-password", methods=['DELETE'])
def delete_password():
  try:
    session = request.headers.get("authorization").split(' ')[1]
    passwordId = request.args.get("id")

    if not session:
      raise Exception("Missing session parameter")
    if not passwordId:
      raise Exception("Missing password id parameter")

    valid, obj = verifySession(session)

    if valid:
      return jsonify(resp(True, "Successfully delete password", deletePassword(obj, passwordId))), 200
    else:
      raise Exception("expired")
  except Exception as err:
    print(err)
    return jsonify(resp(False, "There was an error while trying to get passwords", str(err))), 500

@app.route("/api/update-password", methods=['PUT'])
def update_password():
  try:
    session = request.headers.get('authorization').split(' ')[1]
    passwordId = request.json['id']

    d = {}
    if 'title' in request.json:
      d['title'] = request.json['title']
    if 'username' in request.json:
      d['username'] = request.json['username']
    if 'password' in request.json:
      d['password'] = request.json['password']
    if 'url' in request.json:
      d['url'] = request.json['url']
    if 'email' in request.json:
      d['email'] = request.json['email']
    
    if not session:
      raise Exception("Missing auth header session")
    if not passwordId:
      raise Exception("Missing parameter password id")

    valid, obj = verifySession(session)

    if valid:
      return jsonify(resp(True, "Successfully updated password", updatePassword(obj, passwordId, d))), 200
    else:
      raise Exception("expired")
  except Exception as err:
    print(err)
    return jsonify(resp(False, "There was an error while trying to update passwords", str(err))), 500

@app.route("/api/search-passwords", methods=['GET'])
def search_passwords():
  try:
    session = request.headers.get('authorization').split(' ')[1]
    query = request.args.get('query').lower().split(" ")

    if not session:
      raise Exception("No session provided")
    if not query:
      raise Exception("No search query provided")
    
    valid, obj = verifySession(session)

    if valid:
      return jsonify(resp(True, "Successfully searched password", searchPassword(obj, query))), 200
    else:
      raise Exception("expired")
  except Exception as err:
    print(err)
    return jsonify(resp(False, "There was an error while trying to search passwords", str(err))), 500

# Verifying session
@app.route("/api/verify-session", methods=['GET'])
def verify_session():
  try:
    session = request.headers.get('authorization').split(' ')[1]

    if not session:
      raise Exception("Missing session parameter")

    valid, obj = verifySession(session)

    if valid:
      return jsonify(resp(True, "Session verified")), 200
    else:
      raise Exception("not-verified")
  except Exception as err:
    print(err)
    return jsonify(resp(False, "Could not verify session", str(err))), 500
