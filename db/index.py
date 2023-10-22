import os
from datetime import datetime

from supabase import create_client, Client

from lib.encrypter import checkPassword
from lib.session import createSession

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

#* Create user
def createUser(userId, ip, username, email, hashedPassword, hashKey):
	try:
		supabase.table('users').insert({
			"id": str(userId),
			"ip": ip,
			"username": username,
			"email": email,
			"password": hashedPassword,
			"key": hashKey
		}).execute()
	except Exception as err:
		if err.code == "23505":
			if "username" in err.message:
				raise Exception("exists-username")
			if "email" in err.message:
				raise Exception("exists-email")
			raise Exception("exists")
		raise Exception(err)

#* Login user
def loginUser(ip, username, password):
	data, _ = supabase.table('users').select("id, email, password").eq("username", username).execute()

	if len(data[1]) > 0:
		user = data[1][0]

		if checkPassword(password, user['password']):
			data, _ = supabase.table('users').select("key").eq("username", username).execute()
			hashKey = data[1][0]['key']
			
			token = createSession(user['id'], hashKey)

			supabase.table('logins').insert({
				"token": token,
				"userId": user['id'],
				"date": str(datetime.now()),
				"ip": ip,
				"success": True
			}).execute()

			return token

		else:
			supabase.table('logins').insert({
				"userId": user['id'],
				"date": str(datetime.now()),
				"ip": ip,
				"success": False
			}).execute()

			raise Exception("wrong-credentials")
	else:	
		raise Exception("wrong-credentials")

#* Create Password
def createPassword(userId, title, url, username, email, password):
	data, _ = supabase.table('passwords').insert({
		"userId": userId,
		"title": title.lower(),
		"url": url.lower(),
		"username": username,
		"email": email.lower(),
		"password": password
	}).execute()

	return data

#* Get Passwords
def getPasswords(userId):
	data, _ = supabase.table('passwords').select('*').eq('userId', userId).execute()
	return data[1]

#! Delete Password
def deletePassword(obj, passwordId):
	# checking if it exists
	data, _ = supabase.table('passwords').select("id").eq('userId', obj['id']).eq('id', passwordId).execute()

	if len(data[1]) > 0: # it exists
		data, _ = supabase.table('passwords').delete().eq('id', passwordId).execute()
		if len(data[1]) > 0:
			return data[1][0]
	else:
		raise Exception("Password does not exist")

#* Update Password
def updatePassword(obj, passwordId, update):
	# checking if it exists
	data, _ = supabase.table("passwords").select("*").eq('userId', obj['id']).eq('id', passwordId).execute()

	if len(data[0]) > 0:
		data, _ = supabase.table('passwords').update(update).eq('id', passwordId).execute()
		print(data)
		if len(data[1]) > 0:
			return data[1][0]
	else:
		raise Exception("Password does not exist")
	
#* Search password
def searchPassword(obj, query):
	ids = []
	for word in query:
		title_result, _ = supabase.table("passwords").select("id").ilike('title', f'%{word}%').eq('userId', obj['id']).execute()
		username_result, _ = supabase.table("passwords").select("id").ilike('username', f'%{word}%').eq('userId', obj['id']).execute()
		email_result, _ = supabase.table("passwords").select("id").ilike('email', f'%{word}%').eq('userId', obj['id']).execute()
		website_url_result, _ = supabase.table("passwords").select("id").ilike('url', f'%{word}%').eq('userId', obj['id']).execute()

		for result in title_result[1]:
			ids.append(result['id'])
		for result in username_result[1]:
			ids.append(result['id'])
		for result in email_result[1]:
			ids.append(result['id'])
		for result in website_url_result[1]:
			ids.append(result['id'])

	# getting rid of duplicate ids
	password_ids = sorted(set(ids))

	# fetching the data of all the ids
	data = []
	for password_id in password_ids:
		result, _ = supabase.table("passwords").select("*").eq('id', password_id).execute()
		data.append(result[1][0])

	return data