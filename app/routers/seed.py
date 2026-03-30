from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app import models
import random

router = APIRouter()

@router.get("/seed")
def seed_data(db: Session = Depends(get_db)):
    print("SEED FUNCTION CALLED")

    # -----------------------
    # 1. ADD HOSPITALS
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

    existing = db.query(models.Hospital).all()
    existing_names = [h.name for h in existing]

    for name, city, lat, lon in hospital_data:
        if name not in existing_names:
            db.add(models.Hospital(
                name=name,
                city=city,
                latitude=lat,
                longitude=lon
            ))

    db.commit()

    hospitals = db.query(models.Hospital).all()

    # -----------------------
    # 2. ADD SERVICES
    # -----------------------
    for h in hospitals:
        existing_services = db.query(models.Service).filter(
            models.Service.hospital_id == h.hospital_id
        ).first()

        if not existing_services:
            services = [
                models.Service(hospital_id=h.hospital_id, service_name="blood test", price=400 + h.hospital_id * 50),
                models.Service(hospital_id=h.hospital_id, service_name="x ray", price=700 + h.hospital_id * 60),
                models.Service(hospital_id=h.hospital_id, service_name="mri", price=2500 + h.hospital_id * 100),
                models.Service(hospital_id=h.hospital_id, service_name="ct scan", price=2000 + h.hospital_id * 90),
            ]
            db.add_all(services)

    db.commit()

    # -----------------------
    # 3. ADD DOCTORS + FEES
    # -----------------------
    for h in hospitals:
        doctor_exists = db.query(models.Doctor).filter(
            models.Doctor.hospital_id == h.hospital_id
        ).first()

        if not doctor_exists:
            doctor = models.Doctor(
                name=f"Dr. {h.name.split()[0]}",
                hospital_id=h.hospital_id,
                consultation_fee=500 + h.hospital_id * 50
            )
            db.add(doctor)
            db.commit()
            db.refresh(doctor)

            # -----------------------
            # 4. ADD SLOTS
            # -----------------------
            slots = []
            base_time = datetime(2026, 4, 10, 10, 0)

            for i in range(5):
                slots.append(models.DoctorSlot(
                    doctor_id=doctor.doctor_id,
                    slot_time=base_time + timedelta(hours=i * 2),
                    is_booked=False
                ))

            db.add_all(slots)
            db.commit()

    # -----------------------
    # 5. ADD RATINGS
    # -----------------------
    for h in hospitals:
        review_exists = db.query(models.Review).filter(
            models.Review.hospital_id == h.hospital_id
        ).first()

        if not review_exists:
            for i in range(3):  # 3 reviews per hospital
                review = models.Review(
                    hospital_id=h.hospital_id,
                    rating=random.uniform(3.5, 5.0),
                    review_text="Good hospital"
                )
                db.add(review)

    db.commit()

    return {"message": "Database seeded successfully with hospitals, services, doctors, slots, and reviews"}