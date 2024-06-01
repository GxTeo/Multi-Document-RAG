import os
from typing import List
from pydantic import BaseModel

# Database 
import chromadb
from pymongo import MongoClient
from llama_index.readers.mongodb import SimpleMongoReader

# FastAPI 
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse

# Helper functions
from utils import *

app = FastAPI()
origins = ["*",
           "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ApiKey(BaseModel):
    api_key: str


remote_database = chromadb.HttpClient(host='localhost', port=8000, ssl=False)
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_reader = SimpleMongoReader(host='localhost', port=27017)

try:
    mongo_client.server_info()
    print("Connected to the mongo database")
except Exception as e:
    print("Unable to connect to the mongo database")

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
        os.environ["OPENAI_API_KEY"] =  os.getenv('OPENAI_API_KEY')
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
        # print('Collections:', collections)
        return {"collections": collections}, 200
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

    for file in files:
        filename = file.filename
        file_content = await file.read()
        text = extract_text(filename=filename, content=file_content)
        doc = {'filename': filename, 'upload_time': datetime.now(), 'text': text, 'content': Binary(file_content)}
        documents_collection.insert_one(doc)
    
    return {"detail": "Files uploaded successfully"}, 200


@app.post("/generate_index")
async def generate_index(collection_name: str = Form(...)):
    # lazy import
    from index import QueryEngineTools
    import chromadb
    from llama_index.embeddings.openai import OpenAIEmbedding

    global query_engine_tools
    # Test the connection to the mongo database
    try:
        mongo_client.server_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to connect to the mongo database")
    
    # Test the connection to the chroma database
    try:
        remote_database.get_collections()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to connect to the chroma database")

    try:
        embed_model = OpenAIEmbedding(model="text-embedding-3-small", embed_batch_size=256)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unable to connect to the OpenAI API")

    query_engine_tools = QueryEngineTools(collection_name=collection_name, embed_model=embed_model, mongo_reader=mongo_reader, mongo_client=mongo_client, chroma_client=remote_database, db_name='Documents', top_k=3).get_query_engine_tools()
    
    return {"detail": "Index generated successfully"}, 200

@app.post("/chat_with_agent")
async def chat_with_agent(question: str = Form(...)):
    pass




