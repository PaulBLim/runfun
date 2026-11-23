from pydantic import BaseModel, Field

class RunCreate(BaseModel):
    goal_distance_m: int = Field(gt=0, description="distance of the run in meters")
    goal_time_s: int = Field(gt=0, description="The time of the run in seconds")