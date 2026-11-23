from datetime import datetime
from database import runs
from models import RunCreate

def create_run(run: RunCreate) -> dict:
    document = {
        "goal_distance_m": run.goal_distance_m,
        "goal_time_s": run.goal_time_s,
        "started_at": datetime.now(),
        "finished_at": None,
    }

    result = runs.insert_one(document)

    return {
        "id": str(result.inserted_id),
        "goal_distance_m": run.goal_distance_m,
        "goal_time_s": run.goal_time_s,
        "started_at": datetime.now(),
    }