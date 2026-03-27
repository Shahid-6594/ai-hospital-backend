from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()

@router.get("/hospital-doctors/{hospital_id}")
def get_doctors(hospital_id: int, db: Session = Depends(get_db)):

    doctors = (
        db.query(models.Doctor)
        .filter(models.Doctor.hospital_id == hospital_id)
        .all()
    )

    return doctors