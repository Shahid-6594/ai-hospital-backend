from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app import models

router = APIRouter()

@router.get("/seed")
def seed_data(db: Session = Depends(get_db)):
    print("SEED FUNCTION CALLED")

    # -----------------------
    # 1. HOSPITALS
    # -----------------------
    hospital_data = [
        ("AIIMS Delhi", "Delhi", 28.5672, 77.2100),
        ("Fortis Hospital", "Delhi", 28.5670, 77.2420),
        ("Apollo Hospital", "Delhi", 28.5410, 77.2830),
        ("Max Super Speciality Hospital", "Delhi", 28.5700, 77.2400),
        ("Safdarjung Hospital", "Delhi", 28.5675, 77.2050),
        ("BLK Max Hospital", "Delhi", 28.6448, 77.1897),
        ("Medanta Hospital", "Gurgaon", 28.4395, 77.0400),
        ("Artemis Hospital", "Gurgaon", 28.4500, 77.0850),
        ("Paras Hospital", "Gurgaon", 28.4210, 77.0405),
        ("Columbia Asia Hospital", "Gurgaon", 28.4560, 77.0720),
    ]

    for name, city, lat, lon in hospital_data:
        exists = db.query(models.Hospital).filter(models.Hospital.name == name).first()
        if not exists:
            db.add(models.Hospital(name=name, city=city, latitude=lat, longitude=lon))

    db.commit()

    hospitals = db.query(models.Hospital).all()

    # -----------------------
    # 2. SERVICES
    # -----------------------
    for h in hospitals:
        exists = db.query(models.Service).filter(models.Service.hospital_id == h.hospital_id).first()
        if not exists:
            db.add_all([
                models.Service(hospital_id=h.hospital_id, service_name="blood test", price=400 + h.hospital_id * 50),
                models.Service(hospital_id=h.hospital_id, service_name="x ray", price=700 + h.hospital_id * 60),
                models.Service(hospital_id=h.hospital_id, service_name="mri", price=2500 + h.hospital_id * 100),
                models.Service(hospital_id=h.hospital_id, service_name="ct scan", price=2000 + h.hospital_id * 90),
            ])
    db.commit()

    # -----------------------
    # 3. DOCTORS + SLOTS
    # -----------------------
    for h in hospitals:
        doctor = db.query(models.Doctor).filter(models.Doctor.hospital_id == h.hospital_id).first()

        if not doctor:
            doctor = models.Doctor(
                name=f"Dr. {h.name.split()[0]}",
                hospital_id=h.hospital_id,
                consultation_fee=500 + h.hospital_id * 50
            )
            db.add(doctor)
            db.commit()
            db.refresh(doctor)

            base_time = datetime(2026, 4, 10, 10, 0)
            slots = []

            for i in range(5):
                slots.append(models.DoctorSlot(
                    doctor_id=doctor.doctor_id,
                    slot_time=base_time + timedelta(hours=i * 2),
                    is_booked=False
                ))

            db.add_all(slots)
            db.commit()

    # -----------------------
    # 4. REVIEWS
    # -----------------------
    ratings_data = {
        "AIIMS Delhi": 4.7,
        "Fortis Hospital": 4.5,
        "Apollo Hospital": 4.6,
        "Max Super Speciality Hospital": 4.4,
        "Safdarjung Hospital": 3.9,
        "BLK Max Hospital": 4.3,
        "Medanta Hospital": 4.6,
        "Artemis Hospital": 4.2,
        "Paras Hospital": 4.0,
        "Columbia Asia Hospital": 4.1
    }

    for h in hospitals:
        review = db.query(models.Review).filter(models.Review.hospital_id == h.hospital_id).first()
        if not review:
            db.add(models.Review(
                hospital_id=h.hospital_id,
                rating=ratings_data.get(h.name, 4),
                comment="Good hospital"
            ))

    db.commit()

    return {"message": "Database seeded successfully"}