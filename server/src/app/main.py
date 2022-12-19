from fastapi import FastAPI

from app.routers import files, users

app = FastAPI()

app.include_router(files.router)
app.include_router(users.router)
