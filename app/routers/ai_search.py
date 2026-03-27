from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models
from app.services.query_parser import parse_query
from math import radians, cos, sin, asin, sqrt

router = APIRouter()


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c


@router.post("/ai-search")
def ai_search(data: dict, db: Session = Depends(get_db)):

    query = data["query"]
    user_lat = data["user_lat"]
    user_lon = data["user_lon"]

    print("USER QUERY:", query)

    parsed = parse_query(query)
    print("PARSED:", parsed)

    service = parsed["service"]
    print("SERVICE:", service)

    if not service:
        return []

    # Database Query
    results = (
        db.query(
            models.Hospital.hospital_id,
            models.Hospital.name.label("hospital"),
            models.Service.service_name.label("service"),
            models.Service.price,
            models.Hospital.city,
            models.Hospital.latitude,
            models.Hospital.longitude,
            func.avg(models.Review.rating).label("rating")
        )
        .join(models.Service, models.Service.hospital_id == models.Hospital.hospital_id)
        .outerjoin(models.Review, models.Review.hospital_id == models.Hospital.hospital_id)
        .filter(
            func.replace(func.lower(models.Service.service_name), "-", " ")
            .ilike(f"%{service.lower()}%")
        )
        .group_by(
            models.Hospital.hospital_id,
            models.Hospital.name,
            models.Service.service_name,
            models.Service.price,
            models.Hospital.city,
            models.Hospital.latitude,
            models.Hospital.longitude
        )
        .all()
    )

    print("RAW DB RESULTS:", results)

    response = []

    for r in results:

        # Distance
        if user_lat is not None and user_lon is not None:
            distance = haversine(
                user_lat,
                user_lon,
                float(r.latitude),
                float(r.longitude)
            )
        else:
            distance = 9999

        rating = float(r.rating) if r.rating else 0

        # Score calculation (AI ranking)
        score = (
            (5 - rating) * 2 +
            float(distance) * 0.5 +
            float(r.price) * 0.01
        )

        response.append({
            "hospital_id": r.hospital_id,
            "hospital": r.hospital,
            "service": r.service,
            "price": float(r.price),
            "city": r.city,
            "rating": rating,
            "distance_km": round(distance, 2),
            "latitude": float(r.latitude),
            "longitude": float(r.longitude),
            "score": score
        })

    if len(response) == 0:
        return []

    # Sort by AI score
    response.sort(key=lambda x: x["score"])

    # Tagging
    response[0]["tag"] = "BEST"

    cheapest = min(response, key=lambda x: x["price"])
    cheapest["tag"] = "CHEAPEST"

    closest = min(response, key=lambda x: x["distance_km"])
    closest["tag"] = "CLOSEST"

    # Apply user preference sorting
    if parsed["nearby"]:
        response.sort(key=lambda x: x["distance_km"])

    if parsed["sort_by_price"]:
        response.sort(key=lambda x: x["price"])

    if parsed["sort_by_rating"]:
        response.sort(key=lambda x: x["rating"], reverse=True)

    return response