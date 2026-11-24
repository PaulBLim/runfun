from datetime import datetime
from database import runs
from models import RunCreate, RunPointCeate
from bson import ObjectId
from bson.errors import InvalidId

def create_run(run: RunCreate) -> dict:
    document = {
        "goal_distance_m": run.goal_distance_m,
        "goal_time_s": run.goal_time_s,
        "started_at": datetime.now(),
        "finished_at": None,
        "points": [],
    }

    result = runs.insert_one(document)

    return {
        "id": str(result.inserted_id),
        "goal_distance_m": document["goal_distance_m"],
        "goal_time_s": document["goal_time_s"],
        "started_at": document["started_at"],
        "points": document["points"],
    }

def list_runs() -> list[dict]:
    documents = runs.find()
    return [
        {
            "id": str(document["_id"]),
            "goal_distance_m": document["goal_distance_m"],
            "goal_time_s": document["goal_time_s"],
            "started_at": document["started_at"],
            "finished_at": document["finished_at"],
            "points": document["points"],
        }
        for document in documents
    ]


def get_run(run_id: str) -> dict:
    try:
        mongo_id = ObjectId(run_id)
    except InvalidId:
        return None

    document = runs.find_one({"_id": mongo_id})
    if document is None:
        return None

    return {
        "id": str(document["_id"]),
        "goal_distance_m": document["goal_distance_m"],
        "goal_time_s": document["goal_time_s"],
        "started_at": document["started_at"],
        "finished_at": document["finished_at"],
        "points": document["points"],
    }

def add_run_point(run_id: str, point: RunPointCeate) -> bool:
    try:
        mongo_id = ObjectId(run_id)
    except InvalidId:
        return False

    result = runs.update_one({"_id": mongo_id}, {"$push": {"points": point.model_dump()}})
    return result.matched_count > 0