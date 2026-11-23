from fastapi import FastAPI, status

from models import RunCreate
from repository import create_run

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/runs", status_code=status.HTTP_201_CREATED)
def post_run(run: RunCreate):
    return create_run(run)