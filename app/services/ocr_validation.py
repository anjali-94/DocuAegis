import pytesseract
from pdf2image import convert_from_path
import PyPDF2
from PIL import Image
import os
import re

def extract_text(file_path: str, file_type: str) -> str:
    """
    Extract text from images or PDFs.
    """
    try:
        if file_type in ["image/jpeg", "image/png"]:
            # Extract text from image using pytesseract
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        elif file_type == "application/pdf":
            # Convert PDF to images and extract text
            images = convert_from_path(file_path)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img)
            # Also try extracting text directly from PDF
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
            return text.strip()
        else:
            return ""
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def validate_document(text: str, filename: str) -> dict:
    """
    Validate document for verification or fraud detection.
    Returns a dict with verification status and message.
    """
    # Basic validation rules (customize as needed)
    if not text or len(text.strip()) < 10:
        return {
            "is_verified": False,
            "message": "Document contains insufficient text for verification."
        }

    # Example: Check for specific keywords (e.g., "Official", "ID", "Certificate")
    required_keywords = ["official", "id", "certificate", "government"]
    text_lower = text.lower()
    keyword_found = any(keyword in text_lower for keyword in required_keywords)

    # Example: Check for suspicious patterns (e.g., repeated text, invalid formats)
    suspicious_patterns = [
        r"(\b\w+\b)\s+\1\s+\1",  # Repeated words
        r"[^\w\s.,-]"            # Unusual characters
    ]
    is_suspicious = any(re.search(pattern, text_lower) for pattern in suspicious_patterns)

    if not keyword_found:
        return {
            "is_verified": False,
            "message": "Document lacks required keywords for verification."
        }
    if is_suspicious:
        return {
            "is_verified": False,
            "message": "Document contains suspicious patterns."
        }

    return {
        "is_verified": True,
        "message": "Document appears to be verified."
    }