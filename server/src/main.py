from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def dummy_endpoint():
    return {"Hello": "World"}
