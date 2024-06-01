import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ApiKey(BaseModel):
    api_key: str

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
    


