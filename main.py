from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status

from distance import total_distance_km
from models import RunCreate, RunPointCeate
from repository import add_run_point, create_run, get_run, list_runs
from pace import splits_plan, calculate_progress

app = FastAPI()

def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/runs", status_code=status.HTTP_201_CREATED)
def post_run(run: RunCreate):
    splits = splits_plan(run.goal_distance_km, run.goal_time_minutes)
    run = create_run(run)
    return {**run, "splits": splits}

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
def post_run_point(run_id: str, point: RunPointCeate) -> dict:
    run = add_run_point(run_id, point)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    points = sorted(run["points"], key=lambda x: x["recorded_at"])
    distance_km = total_distance_km(points)
    elapsed_time = _as_utc(points[-1]["recorded_at"]) - _as_utc(run["started_at"])
    elapsed_time_minutes = max(0.0, elapsed_time.total_seconds() / 60)

    progress = calculate_progress(run["goal_distance_km"], run["goal_time_minutes"], distance_km, elapsed_time_minutes)

    return {
        **point.model_dump(),
        "distance_km": distance_km,
        "elapsed_time_minutes": elapsed_time_minutes,
        "progress": progress,
    }

