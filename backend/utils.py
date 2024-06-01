import re 

from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from io import BytesIO

def extract_text(filename: str, content: bytes):
    '''
    Extracts text from a file
    '''
    data = BytesIO(content)
    if filename.endswith('.pdf'):
        pdf = PdfReader(data)
        text = ' '.join(page.extract_text() for page in pdf.pages)
    elif filename.endswith('.docx'):
        docx_doc = DocxDocument(data)
        text = ' '.join(paragraph.text for paragraph in docx_doc.paragraphs)
    return text

def modify_string(s):
    # Remove invalid characters
    s = re.sub('[^a-zA-Z0-9-_]', '', s)
    
    # Replace consecutive periods
    s = re.sub('\.\.+', '.', s)
    
    # Check if the string is a valid IPv4 address
    if re.match('^(\d{1,3}\.){3}\d{1,3}$', s):
        s = 'NotValidIPv4'
    
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