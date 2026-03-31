from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()

@router.get("/debug/services")
def debug_services(db: Session = Depends(get_db)):
    services = db.query(models.Service).all()
    return services

@router.get("/debug/hospitals")
def debug_hospitals(db: Session = Depends(get_db)):
    hospitals = db.query(models.Hospital).all()
    return hospitals

@router.get("/debug/doctors")
def debug_doctors(db: Session = Depends(get_db)):
    doctors = db.query(models.Doctor).all()
    return doctors
@router.get("/debug/reviews")
def get_reviews(db: Session = Depends(get_db)):
    reviews= db.query(models.Review).all()
    return reviews