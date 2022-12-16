from app.routers import files
from fastapi import FastAPI

app = FastAPI()

app.include_router(files.router)
