import re 

from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from io import BytesIO

from llama_parse import LlamaParse
from dotenv import load_dotenv
import os

load_dotenv()
LLAMA_PARSE_API_KEY = os.getenv("LLAMA_PARSE_API_KEY")

parser = LlamaParse(
    api_key=LLAMA_PARSE_API_KEY,  # can also be set in your env as LLAMA_CLOUD_API_KEY
    result_type="markdown",  # "markdown" and "text" are available
    num_workers=4,  # if multiple files passed, split in `num_workers` API calls
    verbose=True,
    language="en",  # Optionally you can define a language, default=en
)

def extract_text(filename: str, content: bytes):
    '''
    Extracts text from a file
    '''
    # data = BytesIO(content)
    documents = parser.load_data(content, extra_info={"file_name": filename})
    text = documents[0].text
    
    return text

def modify_string(s):
    # Remove invalid characters
    s = re.sub('[^a-zA-Z0-9-_]', '', s)
    
    # Replace consecutive periods
    s = re.sub('\.\.+', '.', s)
  
    # Ensure the string length is within 3-63 characters
    if len(s) < 3:
        s += 'abc'
    elif len(s) > 63:
        s = s[:63]
    
    # Ensure the string starts and ends with an alphanumeric character
    if not s[0].isalnum():
        s = 'a' + s[1:]
    if not s[-1].isalnum():
        s = s[:-1] + 'a'
    
    return s