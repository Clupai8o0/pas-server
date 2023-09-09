import jwt
import os

def resp(success, msg, data={}):
  return { 
    "success": success,
    "msg": msg,
    "data": data
  }

def verifySession(session):
  try:
    obj = jwt.decode(session.encode(), os.getenv('SECRET'), algorithms=["HS256"])
    return True, obj
  except Exception as err:
    print(err)
    return False, err
  