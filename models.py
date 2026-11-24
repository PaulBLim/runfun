from pydantic import BaseModel, Field, AwareDatetime

class RunCreate(BaseModel):
    goal_distance_km: float = Field(gt=0, description="distance of the run in kilometers")
    goal_time_minutes: int = Field(gt=0, description="The time of the run in minutes")

class RunPointCeate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy_m: float = Field(ge=0, description="accuracy of the point in meters")
    recorded_at: AwareDatetime