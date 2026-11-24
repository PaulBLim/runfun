from typing import Optional

def pace(distance_km: float, time_minutes: float) -> Optional[float]:
    """Minutes required to cover 1 kilometer."""
    if distance_km <= 0 or time_minutes <= 0:
        return None
    return time_minutes / distance_km

def splits_plan(goal_distance_km: float, goal_time_minutes: int) -> Optional[list[dict]]:
    """Splits plan is a list of distances to cover in each split."""
    if goal_distance_km <= 0 or goal_time_minutes <= 0:
        return None
    distance_splits = list(range(1, int(goal_distance_km) + 1))
    if not distance_splits or distance_splits[-1] != goal_distance_km:
        distance_splits.append(goal_distance_km)
    return [
        {
        "distance_km": distance_km,
        "time_elapsed_minutes": goal_time_minutes * distance_km / goal_distance_km,
        } for distance_km in distance_splits
    ]

def calculate_progress(goal_distance_km: float, goal_time_minutes: int, distance_km: float, time_elapsed_minutes: int) -> Optional[dict]:
    """Compare the distance covered so far with the goal pace.
    """
    if goal_distance_km <= 0 or goal_time_minutes <= 0 or distance_km < 0 or time_elapsed_minutes < 0:
        return None

    expected_minutes = goal_time_minutes * distance_km / goal_distance_km
    minutes_behind = time_elapsed_minutes - expected_minutes
    remianing_km = goal_distance_km - distance_km
    remianing_time = goal_time_minutes - time_elapsed_minutes

    if remianing_km <= 0:
        status = "goal_reached" if remianing_time <= 0 else "goal_missed"
    elif remianing_time <= 0:
        status = "goal_missed"
    elif minutes_behind <= 0.01:
        minutes_behind = 0.0
        status = "on_plan"
    elif minutes_behind > 0:
        status = "behind"
    else:
        status = "ahead"

    return {
        "average_pace_min_per_km": pace(distance_km, time_elapsed_minutes),
        "minutes_behind": minutes_behind,
        "required_pace_min_per_km": pace(remianing_km, remianing_time),
        "status": status,
        "remaining_distance_km": remianing_km,
        "remaining_time_minutes": remianing_time,
    }