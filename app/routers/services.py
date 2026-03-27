from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models
from app.utils.distance import haversine


router = APIRouter()


@router.get("/services")
def search_services(name: str, db: Session = Depends(get_db)):

    services = db.query(models.Service).filter(
        models.Service.service_name.ilike(f"%{name}%")
    ).all()

    return services


@router.get("/search-services")
def search_services_with_hospital(name: str, db: Session = Depends(get_db)):

    results = (
        db.query(
            models.Service.service_name,
            models.Service.price,
            models.Hospital.name.label("hospital_name"),
            models.Hospital.city
        )
        .join(models.Hospital, models.Service.hospital_id == models.Hospital.hospital_id)
        .filter(models.Service.service_name.ilike(f"%{name}%"))
        .all()
    )

    response = []

    for r in results:
        response.append({
            "hospital": r.hospital_name,
            "service": r.service_name,
            "price": r.price,
            "city": r.city
        })

    return response


@router.get("/search-services-advanced")
def search_services_advanced(name: str, db: Session = Depends(get_db)):

    results = (
        db.query(
            models.Service.service_name,
            models.Service.price,
            models.Hospital.name.label("hospital"),
            models.Hospital.city,
            func.avg(models.Review.rating).label("rating")
        )
        .join(models.Hospital, models.Service.hospital_id == models.Hospital.hospital_id)
        .outerjoin(models.Review, models.Hospital.hospital_id == models.Review.hospital_id)
        .filter(models.Service.service_name.ilike(f"%{name}%"))
        .group_by(
            models.Service.service_name,
            models.Service.price,
            models.Hospital.name,
            models.Hospital.city
        )
        .all()
    )

    response = []

    for r in results:
        response.append({
            "hospital": r.hospital,
            "service": r.service_name,
            "price": r.price,
            "city": r.city,
            "rating": r.rating
        })

    return response


@router.get("/search-nearby")
def search_nearby(name: str, user_lat: float, user_lon: float, db: Session = Depends(get_db)):

    results = (
        db.query(
            models.Service.service_name,
            models.Service.price,
            models.Hospital.name,
            models.Hospital.city,
            models.Hospital.latitude,
            models.Hospital.longitude
        )
        .join(models.Hospital, models.Service.hospital_id == models.Hospital.hospital_id)
        .filter(models.Service.service_name.ilike(f"%{name}%"))
        .all()
    )

    response = []

    for r in results:

        distance = haversine(
            user_lat,
            user_lon,
            float(r.latitude),
            float(r.longitude)
        )

        response.append({
            "hospital": r.name,
            "service": r.service_name,
            "price": r.price,
            "city": r.city,
            "distance_km": round(distance, 2)
        })

    response.sort(key=lambda x: x["distance_km"])

    return response