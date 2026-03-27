from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
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

    # Services
    s1 = models.Service(hospital_id=1, service_name="blood test", price=500)
    s2 = models.Service(hospital_id=1, service_name="x ray", price=800)
    s3 = models.Service(hospital_id=2, service_name="mri", price=3000)
    s4 = models.Service(hospital_id=2, service_name="ct scan", price=2500)

    db.add_all([s1, s2, s3, s4])
    db.commit()

    # Doctors
    d1 = models.Doctor(name="Dr. Sharma", hospital_id=1)
    d2 = models.Doctor(name="Dr. Mehta", hospital_id=2)

    db.add_all([d1, d2])
    db.commit()

    # Slots
    slot1 = models.DoctorSlot(doctor_id=1, slot_time="2026-04-01 10:00:00", is_booked=False)
    slot2 = models.DoctorSlot(doctor_id=1, slot_time="2026-04-01 12:00:00", is_booked=False)
    slot3 = models.DoctorSlot(doctor_id=2, slot_time="2026-04-02 11:00:00", is_booked=False)

    db.add_all([slot1, slot2, slot3])
    db.commit()

    return {"message": "Sample data inserted"}