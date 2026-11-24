from datetime import datetime, timezone

from pymongo import ReturnDocument
from database import runs
from models import RunCreate, RunPointCeate
from bson import ObjectId
from bson.errors import InvalidId

def create_run(run: RunCreate) -> dict:
    document = {
        "goal_distance_km": run.goal_distance_km,
        "goal_time_minutes": run.goal_time_minutes,
        "started_at": datetime.now(timezone.utc),
        "finished_at": None,
        "points": [],
    }

    result = runs.insert_one(document)

    return {
        "id": str(result.inserted_id),
        "goal_distance_km": document["goal_distance_km"],
        "goal_time_minutes": document["goal_time_minutes"],
        "started_at": document["started_at"],
        "points": document["points"],
    }

def list_runs() -> list[dict]:
    documents = runs.find()
    return [
        {
            "id": str(document["_id"]),
            "goal_distance_km": document["goal_distance_km"],
            "goal_time_minutes": document["goal_time_minutes"],
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
        "goal_distance_km": document["goal_distance_km"],
        "goal_time_minutes": document["goal_time_minutes"],
        "started_at": document["started_at"],
        "finished_at": document["finished_at"],
        "points": document["points"],
    }

def add_run_point(run_id: str, point: RunPointCeate) -> bool:
    try:
        mongo_id = ObjectId(run_id)
    except InvalidId:
        return False

    result = runs.find_one_and_update({"_id": mongo_id}, {"$push": {"points": point.model_dump()}},
    return_document=ReturnDocument.AFTER )
    return result