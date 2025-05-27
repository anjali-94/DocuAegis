from fastapi import APIRouter, Request, UploadFile, File, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from ..services.database import SessionLocal
from ..services.models import FileUpload
import shutil, os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return request.app.templates.TemplateResponse("dashboard.html", {"request": request})

@router.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_file = FileUpload(
        filename=file.filename,
        filetype=file.content_type,
        filepath=file_path
    )
    db.add(db_file)
    db.commit()

    return request.app.templates.TemplateResponse("result.html", {
        "request": request,
        "filename": file.filename,
        "filetype": file.content_type
    })
