from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

import main

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
def verify_token(token:str,credentials_exception):
 try:
     payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
     username: str = payload.get("sub")
     if username is None:
         raise credentials_exception
     token_data = main.TokenData(username=username)
 except JWTError:
     raise credentials_exception
 
 # return the User object
 user = main.get_user(username=token_data.username)
#  print('User object: ',user)
 return user