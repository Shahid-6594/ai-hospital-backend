from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.services.query_parser import parse_query
from math import radians, cos, sin, asin, sqrt
from sqlalchemy import func

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

    parsed = parse_query(query)

    service = parsed["service"]

    if not service:
        return []

    results = (
        db.query(
            models.Hospital.hospital_id,
            models.Service.service_name,
            models.Service.price,
            models.Hospital.name,
            models.Hospital.city,
            models.Hospital.latitude,
            models.Hospital.longitude,
            func.avg(models.Review.rating).label("rating")
        )
        .join(models.Hospital, models.Service.hospital_id == models.Hospital.hospital_id)
        .outerjoin(models.Review, models.Hospital.hospital_id == models.Review.hospital_id)
        .filter(func.replace(func.lower(models.Service.service_name), "-", " ").like(f"%{service.lower()}%"))
        .group_by(
            models.Hospital.hospital_id,
            models.Service.service_name,
            models.Service.price,
            models.Hospital.name,
            models.Hospital.city,
            models.Hospital.latitude,
            models.Hospital.longitude
        )
        .all()
    )

    response = []

    for r in results:

        if user_lat is not None and user_lon is not None:
            distance = haversine(
                user_lat,
                user_lon,
                float(r.latitude),
            float(r.longitude)
            )
        else:
            distance = 9999  # large distance if location not availableF
        score = (
            (5 - float(r.rating or 0)) * 2 +
            float(distance) * 0.5 +
            float(r.price) * 0.01
        )

        response.append({
            "hospital_id":r.hospital_id,
            "hospital": r.name,
            "service": r.service_name,
            "price": r.price,
            "city": r.city,
            "rating":r.rating,
            "distance_km": round(distance, 2),
            "latitude": float(r.latitude),
            "longitude":float(r.longitude),
            "score":score
        })
    response.sort(key=lambda x: x["score"])
    if len(response) > 0:
        response[0]["tag"] = "⭐ Best Option"
        cheapest = min(response, key=lambda x: x["price"])
        cheapest["tag"] = "💰 Cheapest"

        closest = min(response, key=lambda x: x["distance_km"])
        closest["tag"] = "📍 Closest"
    
    if parsed["nearby"]:
        response.sort(key=lambda x: x["distance_km"])
    
    if parsed["sort_by_price"]:
        response.sort(key=lambda x: x["price"])
    
    if parsed["sort_by_rating"]:
        response.sort(key=lambda x: x.get("rating", 0), reverse=True)

    return response