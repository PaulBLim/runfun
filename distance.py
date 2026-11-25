
from haversine import Unit, haversine


def distance_between_km(first_point: dict, second_point: dict) -> float:
    start = (first_point["latitude"], first_point["longitude"])
    end = (second_point["latitude"], second_point["longitude"])
    return haversine(start, end, unit=Unit.KILOMETERS)

def total_distance_km(points: list[dict]) -> float:
    return sum(
        (distance_between_km(first, second)
         for first, second in zip(points, points[1:])), 0.0)
