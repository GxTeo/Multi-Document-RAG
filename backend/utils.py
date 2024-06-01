from PyPDF2 import PdfFileReader
from docx import Document as DocxDocument
from io import BytesIO

def extract_text(filename: str, content: bytes):
    '''
    Extracts text from a file
    '''
    data = BytesIO(content)
    if filename.endswith('.pdf'):
        pdf = PdfFileReader(data)
        text = ' '.join(page.extractText() for page in pdf.pages)
    elif filename.endswith('.docx'):
        docx_doc = DocxDocument(data)
        text = ' '.join(paragraph.text for paragraph in docx_doc.paragraphs)
    return text