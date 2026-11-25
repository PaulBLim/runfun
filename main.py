from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from distance import total_distance_km
from models import RunCreate, RunPointCeate
from repository import add_run_point, create_run, finish_run, get_run, list_runs
from pace import pace, splits_plan, calculate_progress

app = FastAPI()

app.mount(
    "/run",
    StaticFiles(directory=Path(__file__).parent / "run_page", html=True),
    name="run_page",
)

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
        if get_run(run_id) is  not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Run is already finished")
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

@app.post("/runs/{run_id}/finish", status_code=status.HTTP_200_OK)
def post_finish_run(run_id: str):
    run = finish_run(run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    points = sorted(run["points"], key=lambda x: x["recorded_at"])
    distance_km = total_distance_km(points)

    elapsed_time = run["finished_at"] - run["started_at"]
    elapsed_time_minutes = max(0.0, elapsed_time.total_seconds() / 60)
   
    return {
        "id": run_id,
        "finished_at": run["finished_at"],
        "distance_km": distance_km,
        "elapsed_time_minutes": elapsed_time_minutes,
        "average_pace_minutes_per_km": pace(distance_km, elapsed_time_minutes)
        #add details that does an analysis of the expected run and the actual run

    }

@app.post("/pace/plan")
def preview_plan(goal: RunCreate) -> dict:
    return {
        "splits": splits_plan(goal.goal_distance_km, goal.goal_time_minutes)
    }