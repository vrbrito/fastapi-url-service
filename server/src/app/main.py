from fastapi import FastAPI
from mangum import Mangum

from app.routers import files, users

app = FastAPI(title="URL Service")

app.include_router(files.router)
app.include_router(users.router)

handler = Mangum(app)
