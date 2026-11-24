from fastapi import FastAPI, HTTPException, status

from models import RunCreate, RunPointCeate
from repository import add_run_point, create_run, get_run, list_runs

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/runs", status_code=status.HTTP_201_CREATED)
def post_run(run: RunCreate):
    return create_run(run)

@app.get("/runs")
def read_runs():
    return list_runs()

@app.get("/runs/{run_id}")
def read_run(run_id: str):
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return run

@app.post("/runs/{run_id}/points", status_code=status.HTTP_201_CREATED)
def post_run_point(run_id: str, point: RunPointCeate):
    if not add_run_point(run_id, point):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return point