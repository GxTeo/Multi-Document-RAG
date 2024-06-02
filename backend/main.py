import os
from typing import List
from pydantic import BaseModel
from enum import Enum

# Database 
import chromadb
from pymongo import MongoClient
from llama_index.readers.mongodb import SimpleMongoReader

# FastAPI 
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse

# Helper functions
from utils import *

app = FastAPI()
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

remote_database = chromadb.HttpClient(host='chroma', port=8000)
mongo_client = MongoClient('mongodb://mongodb:27017/')
mongo_reader = SimpleMongoReader(host='mongodb', port=27017)
query_engine_tools_dict = {}

# Endpoint to test the connection to the backend
@app.get('/', response_class=HTMLResponse)
async def root():
    return """
    <html>
        <body>
            <h1>Welcome to Multi-Doc-RAG v1</h1>
        </body>
    </html>
    """

# Endpoint to validate the OpenAI API key
@app.post('/validate_openai_key')
async def validate_openai_key(api_key: ApiKey):
    # lazy import 
    import openai
    from openai import OpenAI
    client = OpenAI(api_key=api_key.api_key)
    try:
        client.models.list()
        # Set the API key in environment variable
        os.environ["OPENAI_API_KEY"] =  api_key.api_key
        return {"detail": "API key is valid"}, 200
    except openai.AuthenticationError as e:
        print('Error message:', e)
        raise HTTPException(status_code=400, detail="Invalid API key")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@app.get('/get_collections')
async def get_collections():
    try:
        collections = mongo_client['Documents'].list_collection_names()

        # I want to split the collections into two groups: indexed and non-indexed
        indexed_collections = []
        non_indexed_collections = []

        for collection in collections:
            metadata_collection = mongo_client['Documents']['metadata']
            metadata = metadata_collection.find_one({'collection_name': collection})
            if metadata:
                if metadata['indexed'] and collection != 'metadata':
                    indexed_collections.append(collection)
                elif not metadata['indexed'] and collection != 'metadata':
                    non_indexed_collections.append(collection)

        # Return the collections based on the indexed status
        return {"indexed_collections": indexed_collections, "non_indexed_collections": non_indexed_collections, 'status': 200}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to retrieve collections name")

# Endpoint to save the uploaded files into the mongo database
@app.post("/upload_files")
async def upload_files(collection_name: str = Form(...), files: List[UploadFile] = File(...)):
    # lazy import
    from datetime import datetime
    from bson.binary import Binary

    # Test the connection to the mongo database
    try:
        mongo_client.server_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to connect to the database")
    
    for file in files:
        _, ext = os.path.splitext(file.filename)
        if ext.lower() not in ['.pdf', '.docx']:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX files are allowed.")
    
    # Read the document and save into the mongo database collection
    documents_database = mongo_client['Documents']
    documents_collection = documents_database[collection_name]

    # Set Indexed to False for the collection
    metadata_collection = documents_database['metadata']
    metadata_collection.update_one({'collection_name': collection_name}, {"$set": {"indexed": False}}, upsert=True)

    for file in files:
        filename = file.filename
        file_content = await file.read()
        text = extract_text(filename=filename, content=file_content)
        doc = {'filename': filename, 'upload_time': datetime.now(), 'text': text, 'content': Binary(file_content)}
        documents_collection.insert_one(doc)
    
    return {"detail": "Files uploaded successfully"}, 200

@app.get('/display_collections')
async def display_collections():
    try:
        collections = mongo_client['Documents'].list_collection_names()
        collection_dict = {}
        for collection in collections:
            # Extract  the filename for each document in the collection
            collection_list = []
            for file in mongo_client['Documents'][collection].find():
                if 'filename' in file:
                    collection_list.append(file['filename'])
            
            # Add the collection to the dictionary if it has documents
            if len(collection_list) > 0:
                collection_dict[collection] = collection_list
        return collection_dict
    except Exception as e:
        print(f"Unable to retrieve the collections. Error: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve the collections")

# Endpoint to delete a collection from the mongo database and the chroma database
@app.delete('/delete_collection')
async def delete_collection(collection_name: str = Query(...)):
    try:
        for file in mongo_client['Documents'][collection_name].find():
            # Check if file has filename attributes in the mongo collection
            if 'filename' in file and modify_string(file['filename']) in remote_database.list_collections():
                remote_database.delete_collection(modify_string(file['filename']))
            else:
                pass
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to remove the collection from the chroma database")
        
    try:
        mongo_client['Documents'].drop_collection(collection_name)
        metadata_collection = mongo_client['Documents']['metadata']
        metadata_collection.delete_one({'collection_name': collection_name})

        # Drop the chat history for the collection
        chat_history_collection = mongo_client['Documents'][collection_name]['chat_history']
        chat_history_collection.drop()

    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to remove the collection from MongoDB")
    
    try:
        if collection_name in query_engine_tools_dict:
            query_engine_tools_dict.pop(collection_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to remove the collection from the query engine tools dictionary")
    
    return {"detail": "Collection removed successfully"}, 200


@app.post("/generate_index")
async def generate_index(collection_name: str = Form(...)):
    # lazy import
    from index import QueryEngineTools
    from llama_index.embeddings.openai import OpenAIEmbedding
    
    # Test the connection to the mongo database
    try:
        mongo_client.server_info()
    except Exception as e:
        print("Unable to connect to the mongo database")
        raise HTTPException(status_code=500, detail="Unable to connect to the mongo database")
    
    # Test the connection to the chroma database
    try:
        remote_database.list_collections()
    except Exception as e:
        print("Unable to connect to the chroma database")
        raise HTTPException(status_code=500, detail="Unable to connect to the chroma database")

    try:
        embed_model = OpenAIEmbedding(model="text-embedding-3-small", embed_batch_size=256)
    except Exception as e:
        print("Unable to connect to the OpenAI API")
        raise HTTPException(status_code=500, detail="Unable to connect to the OpenAI API")

    query_engine_tools = QueryEngineTools(collection_name=collection_name, embed_model=embed_model, mongo_reader=mongo_reader, mongo_client=mongo_client, chroma_client=remote_database, db_name='Documents', top_k=3).get_query_engine_tools()
    # If the collection has been indexed, set a boolean flag to True in MongoDB
    metadata_collection = mongo_client['Documents']['metadata']
    metadata_collection.update_one({'collection_name': collection_name}, {"$set": {"indexed": True}}, upsert=True)

    query_engine_tools_dict[collection_name] = query_engine_tools
    return {"detail": "Index generated successfully"}, 200

@app.get("/get_chat_history", response_model=List[Messages])
async def get_chat_history(collection_name: str = Query(...)):
    if not collection_name:
        raise HTTPException(status_code=400, detail="Collection name is required")

    try:
        collection = mongo_client['Documents'][collection_name]
        chat_history = collection['chat_history']
        chat_history = chat_history.find()
        chat_history_list = []
        for chat in chat_history:
            user_message = Messages(text=chat['message']['content'], sender=chat['message']['role'])
            chat_history_list.append(user_message)

            # Append assistant response
            assistant_response = Messages(text=chat['response']['content'], sender=chat['response']['role'])
            chat_history_list.append(assistant_response)
        
        return chat_history_list
    
    except Exception as e:
        print(f"Unable to retrieve the chat history from the mongo database. Error: {e}")
        raise HTTPException(status_code=500, detail=f"Unable to retrieve the chat history from the mongo database.")




@app.post("/chat_with_agent")
async def chat_with_agent(message: str = Form(...), collection_name: str = Form(...)):
    # lazy import
    from llama_index.core.agent import ReActAgent
    from llama_index.llms.openai import OpenAI
    from llama_index.core.memory import ChatMemoryBuffer
    from llama_index.core.base.llms.types import ChatMessage
    from llama_index.core import Settings


    # Retrieve any chat history from the mongo database for the collection if it exists
    try:
        collection = mongo_client['Documents'][collection_name]
        chat_history = collection['chat_history']
        chat_history = chat_history.find()
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
    llm = OpenAI(model="gpt-3.5-turbo")
    Settings.llm = llm

    print(f"Chat history: {chat_history_list}")
    agent_instruct = ReActAgent.from_tools(query_engine_tools, llm=llm, verbose=True, chat_history=chat_history_list)

    try:
        response = agent_instruct.chat(message)
        print(str(response))
        # Create ChatMessage instances
        user_message = ChatMessage(role=MessageRole.USER, content=message)
        assistant_response = ChatMessage(role=MessageRole.ASSISTANT, content=response.response)

        try:
            # Save the chat history into the mongo database for the collection
            collection = mongo_client['Documents'][collection_name]
            chat_history = collection['chat_history']
            chat_history.insert_one({
                'message': user_message.dict(),
                'response': assistant_response.dict()
            })

        except Exception as e:
            print(f"Unable to save the chat history into the mongo database. Error: {e}")
            raise HTTPException(status_code=500, detail=f"Unable to save the chat history into the mongo database. Error: {e}")
        
        return {"response": str(response)}, 200
    
    except Exception as e:
        print(f"Unable to chat with the agent. Error: {e}")
        raise HTTPException(status_code=500, detail=f"Unable to chat with the agent. Error: {e}")




