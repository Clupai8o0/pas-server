import os
import jwt
import datetime
import json

from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# setup tables

# insert some basic values

# create functions for selecting/inserting/updating/deleting

#* Insert
#* Create user
def createUser(id, ip, username, email, password, hash, hashKey):
	# todo: error handling, rename this function
	# todo:  user already exists error

	user, session = supabase.auth.sign_up({
		"email": email,
		"password": password
	})
	data, count = supabase.table('users').insert({
		"id": user[1].id,
		"ip": json.dumps([ip]),
		"username": username,
		"email": email,
		"password": hash,
		"key": hashKey
	}).execute()
	token = jwt.encode({
		"id": f"{id}",
		"supabase-token": f"{session[1].access_token}", 
		"hash-key": hashKey,
		"exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=3)
	}, os.getenv('SECRET'), algorithm="HS256")

	return token

#* Login user
def loginUser():
	return


#* Get User
def getUser():
	return
	

#* Passwords
#* Create Password
# todo: update policies to give access only to authenticated specific users
def createPassword(id, title, url, username, email, password):
	print(id, title, url, username, email, password)
	data, count = supabase.table('passwords').insert({
		"userId": id,
		"title": title,
		"url": url,
		"username": username,
		"email": email,
		"password": password
	}).execute()

	return data

#* Get Passwords
def getPasswords(obj):
	data, count = supabase.table('passwords').select('*').eq('userId', obj['id']).execute()
	return data