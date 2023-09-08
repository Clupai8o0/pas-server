from cryptography.fernet import Fernet
import bcrypt
import os

def encrypt(password):
  fernet = Fernet(os.getenv('KEY'))
  return fernet.encrypt(password.encode())

def decrypt(hash):
  fernet = Fernet(os.getenv('KEY'))
  return fernet.decrypt(hash).decode()

def generateKey():
  return Fernet.generate_key()

#todo: organize and change these names they're annoying
def hashPw(password):
  password = password.encode()
  return (bcrypt.hashpw(password, bcrypt.gensalt(8))).decode() #todo: increase the gensalt rounds?

def checkPw(password, hash):
  return bcrypt.checkpw(password.encode(), hash.encode())