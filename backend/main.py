import os
from typing import List

# Load .env file
from dotenv import load_dotenv
load_dotenv()

# Database 
import chromadb
from pymongo import MongoClient
from llama_index.readers.mongodb import SimpleMongoReader

# FastAPI 
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query, Depends, Request,status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse

# Authentication
from hashing import Hash
from oauth import get_current_user
from jwttoken import create_access_token
from fastapi.security import OAuth2PasswordRequestForm

# Asyncio
import nest_asyncio
nest_asyncio.apply()

# Helper functions
from utils import *

# Classes
from classes import User, Login, Token, TokenData, ApiKey, Messages, MessageRole

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REMOTE_DATABASE = chromadb.HttpClient(host='chroma', port=8000)
MONGO_CLIENT = MongoClient('mongodb://mongodb:27017/')
MONGO_READER = SimpleMongoReader(host='mongodb', port=27017)
query_engine_tools_dict = {}

def validate_username(username: str):
    # Username must be between 4 and 20 characters
    if len(username) < 4 or len(username) > 20:
        return False
    
    # Username must not contain special characters
    if not username.isalnum():
        return False
    
    return True

def get_user(username: str):
    user_db = MONGO_CLIENT["Users"]
    user_collection = user_db["users"]
    user = user_collection.find_one({"username": username})

    username = user["username"]
    password = user["password"]
    user_object = User(username=username, password=password)
    return user_object

# Endpoint to test the connection to the backend
@app.get('/', response_class=HTMLResponse)
async def root():
    html_content = """
    <html>
        <body>
            <h1>Welcome to Multi-Doc-RAG v1</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.post('/validate-token')
async def validate_token(current_user: User = Depends(get_current_user)):
    return JSONResponse(content={"detail": "Token is valid"}, status_code=200)


@app.post('/register')
async def create_user(request:User):
    hashed_pass = Hash.bcrypt(request.password)
    user_object = dict(request)
    user_object["password"] = hashed_pass
    user_db = MONGO_CLIENT["Users"]

    try:
        user_collection = user_db["users"]

        # Username validation (Username must be between 4 and 20 characters and must not contain special characters)
        if not validate_username(request.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username. Username must be between 4 and 20 characters and must not contain special characters")
        
        # Password validation (Password must be at least 8 characters and contain at least one special character)
        if len(request.password) < 8 or not any(char in "!@#$%^&*()-_+=~`[]{}|;:,.<>?/" for char in request.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password. Password must be at least 8 characters and contain at least one special character")

        # Check if the username already exists
        if user_collection.find_one({"username":request.username}):
            # raise an error indicating the user already exists
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please use a different username")
        
        # Insert the user into the database
        # print(f"Inserting user object: {user_object}")
        result = user_collection.insert_one(user_object)
        # inserted_user = user_collection.find_one({"_id": result.inserted_id})
        # print(f"Retrieved inserted user: {inserted_user}")

    except Exception as e:
        print(f"Unable to create user. Error: {e}")
        # raise the error if the user cannot be created
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    
    return JSONResponse(content={"detail": "User created successfully"}, status_code=200)

@app.post('/login')
async def login(request:OAuth2PasswordRequestForm = Depends()):

    try:
        user_db = MONGO_CLIENT["Users"]
        user_collection = user_db["users"]
        user = user_collection.find_one({"username":request.username})
        error_msg = {"error": "Invalid credentials"}
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        if not Hash.verify(user["password"],request.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error_msg)
    except Exception as e:
        print(f"Unable to login. Error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    access_token = create_access_token(data={"sub": user["username"] })
    return JSONResponse(content={"access_token": access_token, "token_type": "bearer"}, status_code=200)

# Endpoint to validate the OpenAI API key
@app.post('/validate_openai_key')
async def validate_openai_key(api_key: ApiKey, current_user: User = Depends(get_current_user)):
    # lazy import 
    import openai
    from openai import OpenAI
    client = OpenAI(api_key=api_key.api_key)

    current_username = current_user.username
    try:
        client.models.list()

        # Save the API key in MONGO database
        user_db = MONGO_CLIENT["Users"]
        user_collection = user_db["users"]

        user_collection.update_one({"username": current_username}, {"$set": {"openai_key": api_key.api_key}}, upsert=True)
        return JSONResponse(content={"detail": "API key is valid"}, status_code=200)
    
    except openai.AuthenticationError as e:
        print('Error message:', e)
        raise HTTPException(status_code=401, detail="Invalid API key")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@app.get('/get_openai_key')
async def get_openai_key(current_user: User = Depends(get_current_user)):

    # Retrieve the OpenAI API key from the MONGO database
    current_username = current_user.username
    try:
        user_db = MONGO_CLIENT["Users"]
        user_collection = user_db["users"]
        user = user_collection.find_one({"username": current_username})
        if user:
            api_key = user["openai_key"]
        else:
            api_key = None
        return JSONResponse(content={"api_key": api_key}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to retrieve the OpenAI API key")
    

    
@app.get('/get_collections')
async def get_collections(current_user: User = Depends(get_current_user)):
    current_username = current_user.username
    try:
        collections = MONGO_CLIENT['Documents'].list_collection_names()
        # I want to split the collections into two groups: indexed and non-indexed
        indexed_collections = []
        non_indexed_collections = []

        for collection in collections:
            metadata_collection = MONGO_CLIENT['Documents']['metadata']
            metadata = metadata_collection.find_one({'collection_name': collection, 'username': current_username})
            if metadata:
                if metadata['indexed'] and collection != 'metadata':
                    indexed_collections.append(collection)
                elif not metadata['indexed'] and collection != 'metadata':
                    non_indexed_collections.append(collection)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to retrieve collections name")
    
    # Return the collections based on the indexed status
    return JSONResponse(content={"indexed_collections": indexed_collections, "non_indexed_collections": non_indexed_collections}, status_code=200)

# Endpoint to save the uploaded files into the mongo database
@app.post("/upload_files")
async def upload_files(collection_name: str = Form(...), files: List[UploadFile] = File(...), current_user: User = Depends(get_current_user)):
    # lazy import
    from datetime import datetime
    from bson.binary import Binary

    current_username = current_user.username
    # Test the connection to the mongo database
    try:
        MONGO_CLIENT.server_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to connect to the database")
    
    for file in files:
        _, ext = os.path.splitext(file.filename)
        if ext.lower() not in ['.pdf', '.docx']:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX files are allowed.")
    
    # Read the document and save into the mongo database collection
    documents_database = MONGO_CLIENT['Documents']
    documents_collection = documents_database[collection_name]

    # Set Indexed to False for the collection
    metadata_collection = documents_database['metadata']
    metadata_collection.update_one({'collection_name': collection_name, 'username': current_username}, {"$set": {"indexed": False}}, upsert=True)

    for file in files:
        filename = file.filename
        file_content = await file.read()
        text = extract_text(filename=filename, content=file_content)
        doc = {'filename': filename, 'upload_time': datetime.now(), 'text': text, 'content': Binary(file_content), 'username': current_username}
        documents_collection.insert_one(doc)
    
    return JSONResponse(content={"detail": "Files uploaded successfully"}, status_code=200)

@app.get('/display_collections')
async def display_collections(current_user: User = Depends(get_current_user)):
    current_username = current_user.username
    try:
        collections = MONGO_CLIENT['Documents'].list_collection_names()
        collection_dict = {}
        for collection in collections:
            # Extract  the filename for each document in the collection
            collection_list = []
            for file in MONGO_CLIENT['Documents'][collection].find({'username': current_username}):
                if 'filename' in file:
                    collection_list.append(file['filename'])
            
            # Add the collection to the dictionary if it has documents
            if len(collection_list) > 0:
                collection_dict[collection] = collection_list
        
    except Exception as e:
        # print(f"Unable to retrieve the collections. Error: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve the collections")
    
    return JSONResponse(content=collection_dict, status_code=200)

# Endpoint to delete a collection from the mongo database and the chroma database
@app.delete('/delete_collection')
async def delete_collection(collection_name: str = Query(...), current_user: User = Depends(get_current_user)):
    current_username = current_user.username
    try:
        for file in MONGO_CLIENT['Documents'][collection_name].find({'username': current_username}):
            if 'filename' in file:
                chroma_collection_name = f"{modify_string(file['filename'])}_{current_username}"
                if 'filename' in file and REMOTE_DATABASE.get_collection(name=chroma_collection_name):
                    REMOTE_DATABASE.delete_collection(name=chroma_collection_name)
                else:
                    print('File does not exist in chroma database')

    except Exception as e:
        print(f"Unable to remove the collection from the chroma database. Error: {e}")
        raise HTTPException(status_code=500, detail="Unable to remove the collection from the chroma database")
        
    try:
        document_collection = MONGO_CLIENT['Documents'][collection_name]
        deleted_files = document_collection.delete_many({'username': current_username})
        metadata_collection = MONGO_CLIENT['Documents']['metadata']
        metadata_collection.delete_one({'collection_name': collection_name, 'username': current_username})
    except Exception as e:
        print(f"Unable to remove the collection from MongoDB. Error: {e}")
        raise HTTPException(status_code=500, detail="Unable to remove the collection from MongoDB")
    
    try:
        chat_history = MONGO_CLIENT['Documents'][collection_name]['chat_history']
        result = chat_history.delete_many({'username': current_username})
        if result.deleted_count > 0:
            print(f"Successfully deleted {result.deleted_count} chat history entries for user {current_username}")
        else:
            print(f"No chat history found for user {current_username}")

    except Exception as e:
        print(f"Unable to remove the chat history from the mongo database. Error: {e}")
        raise HTTPException(status_code=500, detail="Unable to remove the chat history from the mongo database")    
    try:
        if collection_name in query_engine_tools_dict:
            query_engine_tools_dict.pop(collection_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to remove the collection from the query engine tools dictionary")
    
    return JSONResponse(content={"detail": "Collection deleted successfully"}, status_code=200)


@app.post("/generate_index")
async def generate_index(collection_name: str = Form(...), current_user: User = Depends(get_current_user)):
    # lazy import
    from index import QueryEngineTools
    from llama_index.embeddings.openai import OpenAIEmbedding
    
    current_username = current_user.username
    api_key = MONGO_CLIENT['Users']['users'].find_one({'username': current_username})['openai_key']

    # Test the connection to the mongo database
    try:
        MONGO_CLIENT.server_info()
    except Exception as e:
        print(f"Unable to connect to the mongo database Error: {e}")
        raise HTTPException(status_code=500, detail="Unable to connect to the mongo database")
    
    # Test the connection to the chroma database
    try:
        REMOTE_DATABASE.heartbeat()
    except Exception as e:
        print(f"Unable to connect to the chroma database Error: {e}", )
        raise HTTPException(status_code=500, detail="Unable to connect to the chroma database")

    try:
        embed_model = OpenAIEmbedding(model="text-embedding-3-small", embed_batch_size=256, api_key=api_key)
    except Exception as e:
        print("Unable to connect to the OpenAI API")
        raise HTTPException(status_code=500, detail="Unable to connect to the OpenAI API")

    query_engine_tools = QueryEngineTools(collection_name=collection_name, embed_model=embed_model, mongo_reader=MONGO_READER, mongo_client=MONGO_CLIENT, chroma_client=REMOTE_DATABASE, db_name='Documents', top_k=3, username=current_username).get_query_engine_tools()
    # If the collection has been indexed, set a boolean flag to True in MongoDB
    metadata_collection = MONGO_CLIENT['Documents']['metadata']
    metadata_collection.update_one({'collection_name': collection_name, 'username': current_username}, {"$set": {"indexed": True}}, upsert=True)

    query_engine_tools_dict[collection_name] = query_engine_tools
    return JSONResponse(content={"detail": "Index generated successfully"}, status_code=200)

@app.get("/get_chat_history", response_model=List[Messages])
async def get_chat_history(collection_name: str = Query(...), current_user: User = Depends(get_current_user)):
    
    current_username = current_user.username
    if not collection_name:
        raise HTTPException(status_code=400, detail="Collection name is required")

    try:
        collection = MONGO_CLIENT['Documents'][collection_name]
        chat_history = collection['chat_history']
        chat_history = chat_history.find({'username': current_username})
        chat_history_list = []
        for chat in chat_history:
            user_message = Messages(text=chat['message']['content'], sender=chat['message']['role'])
            chat_history_list.append(user_message)

            # Append assistant response
            assistant_response = Messages(text=chat['response']['content'], sender=chat['response']['role'])
            chat_history_list.append(assistant_response)

    except Exception as e:
        print(f"Unable to retrieve the chat history from the mongo database. Error: {e}")
        raise HTTPException(status_code=500, detail=f"Unable to retrieve the chat history from the mongo database.")
    
    return chat_history_list

@app.post("/chat_with_agent")
async def chat_with_agent(message: str = Form(...), collection_name: str = Form(...), current_user: User = Depends(get_current_user)):
    # lazy import
    from llama_index.core.agent import ReActAgent
    from llama_index.llms.openai import OpenAI
    from llama_index.core.memory import ChatMemoryBuffer
    from llama_index.core.base.llms.types import ChatMessage
    from llama_index.core import Settings
    from llama_index.llms.sagemaker_endpoint import SageMakerLLM

    ENDPOINT_NAME = "Qwen2-5-72B-Instruct-2024-09-30-06-11-33"
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    REGION_NAME = os.getenv("AWS_DEFAULT_REGION")

    current_username = current_user.username
    api_key = MONGO_CLIENT['Users']['users'].find_one({'username': current_username})['openai_key']

    # Retrieve any chat history from the mongo database for the collection if it exists
    try:
        collection = MONGO_CLIENT['Documents'][collection_name]
        chat_history = collection['chat_history']
        chat_history = chat_history.find({'username': current_username})
        chat_history_list = []
        for chat in chat_history:
            user_message = ChatMessage(
                role=MessageRole.USER,
                content=chat['message']['content'],
                additional_kwargs=chat['message'].get('additional_kwargs', {})
            )
            chat_history_list.append(user_message)

            # Append assistant response
            assistant_response = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=chat['response']['content'],
                additional_kwargs=chat['response'].get('additional_kwargs', {})
            )
            chat_history_list.append(assistant_response)


    except Exception as e:
        print(f"Unable to retrieve the chat history from the mongo database. Error: {e}")
        raise HTTPException(status_code=500, detail=f"Unable to retrieve the chat history from the mongo database. Error: {e}")

    try:
        if query_engine_tools_dict:
            query_engine_tools = query_engine_tools_dict[collection_name]
        else:
            print('Query engine tools dict not defined')
            raise HTTPException(status_code=400, detail="The collection has not been indexed. Please generate the index first.")
    except KeyError:
        print('KeyError: The collection has not been indexed. Please generate the index first.')
        raise HTTPException(status_code=400, detail="The collection has not been indexed. Please generate the index first.")
    
    # Based on experience, gpt-4 is more suitable to behave as agent than gpt-3.5-turbo
    llm = OpenAI(model="gpt-4o", api_key=api_key)
    Settings.llm = llm

    # llm = SageMakerLLM(
    #     endpoint_name=ENDPOINT_NAME,
    #     aws_access_key_id=AWS_ACCESS_KEY_ID,
    #     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    #     region_name=REGION_NAME,
    # )
    # Settings.llm = llm
    # print(f"Chat history: {chat_history_list}")
    agent_instruct = ReActAgent.from_tools(query_engine_tools, llm=llm, verbose=True, chat_history=chat_history_list)

    try:
        response = agent_instruct.chat(message)
        # Create ChatMessage instances
        user_message = ChatMessage(role=MessageRole.USER, content=message)
        assistant_response = ChatMessage(role=MessageRole.ASSISTANT, content=response.response)

        try:
            # Save the chat history into the mongo database for the collection
            collection = MONGO_CLIENT['Documents'][collection_name]
            chat_history = collection['chat_history']
            chat_history.insert_one({
                'message': user_message.dict(),
                'response': assistant_response.dict(),
                'username': current_username
            })

        except Exception as e:
            print(f"Unable to save the chat history into the mongo database. Error: {e}")
            raise HTTPException(status_code=500, detail=f"Unable to save the chat history into the mongo database. Error: {e}")
            
    except Exception as e:
        print(f"Unable to chat with the agent. Error: {e}")
        raise HTTPException(status_code=500, detail=f"Unable to chat with the agent. Error: {e}")
    return JSONResponse(content={"response": str(response)}, status_code=200)





