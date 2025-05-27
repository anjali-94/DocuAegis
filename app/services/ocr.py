# app/services/ocr.py
import pytesseract
from PIL import Image
import io

def process(file):
    image = Image.open(io.BytesIO(file.file.read()))
    text = pytesseract.image_to_string(image)
    return {"extracted_text": text}
