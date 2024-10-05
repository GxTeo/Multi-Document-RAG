from pydantic import BaseModel
from typing import Optional
from enum import Enum

class User(BaseModel):
    username: str
    password: str
class Login(BaseModel):
    username: str
    password: str
class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username: Optional[str] = None
class ApiKey(BaseModel):
    api_key: str

# Chat History 
class MessageRole(str, Enum):
    USER = 'user'
    SYSTEM = 'system'
    ASSISTANT = 'assistant'

# Past Chat Messages 
class Messages(BaseModel):
    text: str
    sender: str