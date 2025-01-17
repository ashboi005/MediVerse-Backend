# file_upload.py
import os
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
from tempfile import NamedTemporaryFile

def handle_file_upload(file):
    # Save the file to a temporary location
    temp_file = NamedTemporaryFile(delete=False)
    temp_file.write(file.read())
    temp_file.close()

    file_path = temp_file.name
    file_extension = file.filename.split('.')[-1].lower()

    # Extract text based on file type (PDF or Image)
    if file_extension == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension in ['jpg', 'jpeg', 'png']:
        return extract_text_from_image(file_path)
    else:
        return "Unsupported file format"

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_image(file_path):
    img = Image.open(file_path)
    text = pytesseract.image_to_string(img)
    return text
