from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()

@router.get("/map-hospitals")
def map_hospitals(db: Session = Depends(get_db)):

    hospitals = db.query(models.Hospital).all()

    response = []

    for h in hospitals:
        response.append({
            "name": h.name,
            "city": h.city,
            "latitude": h.latitude,
            "longitude": h.longitude
        })

    return response