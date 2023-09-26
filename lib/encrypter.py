from cryptography.fernet import Fernet
import os
import bcrypt

# Password hasher
def hashPassword(password):
  password = password.encode()
  return (bcrypt.hashpw(password, bcrypt.gensalt(8))).decode()

def checkPassword(password, hash):
  return bcrypt.checkpw(password.encode(), hash.encode())

# Password encrypt er
def encrypt(password, key):
  fernet = Fernet(key.encode())
  return (fernet.encrypt(password.encode())).decode()

def decrypt(password, key):
  fernet = Fernet(key.encode())
  return fernet.decrypt(password.encode()).decode()

def generateKey():
  return (Fernet.generate_key()).decode()