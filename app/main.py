from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from app.routes import home

app = FastAPI()

# Include routes
app.include_router(home.router)

# Mount templates (optional if using static files)
templates = Jinja2Templates(directory="app/templates")
