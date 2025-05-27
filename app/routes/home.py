from fastapi import APIRouter, Request, UploadFile, File, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from ..services.database import SessionLocal
from ..services.models import FileUpload
from ..services.ocr_validation import extract_text, validate_document
import shutil
import os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    # Fetch all uploaded files for display
    files = db.query(FileUpload).all()
    return request.app.templates.TemplateResponse("dashboard.html", {
        "request": request,
        "files": files
    })

@router.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text and validate
    text = extract_text(file_path, file.content_type)
    validation_result = validate_document(text, file.filename)

    # Save to database
    db_file = FileUpload(
        filename=file.filename,
        filetype=file.content_type,
        filepath=file_path,
        is_verified=validation_result["is_verified"],
        verification_message=validation_result["message"]
    )
    db.add(db_file)
    db.commit()

    return request.app.templates.TemplateResponse("result.html", {
        "request": request,
        "filename": file.filename,
        "filetype": file.content_type,
        "is_verified": validation_result["is_verified"],
        "message": validation_result["message"]
    })