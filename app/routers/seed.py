from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app import models

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/seed")
def seed_data(db: Session = Depends(get_db)):

    # Hospitals
    h1 = models.Hospital(name="City Hospital", city="Delhi", latitude=28.6139, longitude=77.2090)
    h2 = models.Hospital(name="Metro Hospital", city="Delhi", latitude=28.7041, longitude=77.1025)

    db.add_all([h1, h2])
    db.commit()
    db.refresh(h1)
    db.refresh(h2)

    # Services
    s1 = models.Service(hospital_id=h1.hospital_id, service_name="blood test", price=500)
    s2 = models.Service(hospital_id=h1.hospital_id, service_name="x ray", price=800)
    s3 = models.Service(hospital_id=h2.hospital_id, service_name="mri", price=3000)
    s4 = models.Service(hospital_id=h2.hospital_id, service_name="ct scan", price=2500)

    db.add_all([s1, s2, s3, s4])
    db.commit()

    # Doctors
    d1 = models.Doctor(name="Dr. Sharma", hospital_id=h1.hospital_id)
    d2 = models.Doctor(name="Dr. Mehta", hospital_id=h2.hospital_id)

    db.add_all([d1, d2])
    db.commit()
    db.refresh(d1)
    db.refresh(d2)

    # Slots (use datetime, not string)
    slot1 = models.DoctorSlot(doctor_id=d1.doctor_id, slot_time=datetime(2026, 4, 1, 10, 0), is_booked=False)
    slot2 = models.DoctorSlot(doctor_id=d1.doctor_id, slot_time=datetime(2026, 4, 1, 12, 0), is_booked=False)
    slot3 = models.DoctorSlot(doctor_id=d2.doctor_id, slot_time=datetime(2026, 4, 2, 11, 0), is_booked=False)

    db.add_all([slot1, slot2, slot3])
    db.commit()

    return {"message": "Sample data inserted successfully"}