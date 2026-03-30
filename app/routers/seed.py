from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app import models

router = APIRouter()

@router.get("/seed")
def seed_data(db: Session = Depends(get_db)):
    print("SEED FUNCTION CALLED")

    hospital_names = [
        "AIIMS Delhi",
        "Fortis Hospital",
        "Apollo Hospital",
        "Max Super Speciality Hospital",
        "Safdarjung Hospital",
        "BLK Max Hospital",
        "Medanta Hospital",
        "Artemis Hospital",
        "Paras Hospital",
        "Columbia Asia Hospital",
    ]

    existing_hospitals = db.query(models.Hospital).all()
    existing_names = [h.name for h in existing_hospitals]

    new_hospitals = [
        models.Hospital(name="AIIMS Delhi", city="Delhi", latitude=28.5672, longitude=77.2100),
        models.Hospital(name="Fortis Hospital", city="Delhi", latitude=28.5670, longitude=77.2420),
        models.Hospital(name="Apollo Hospital", city="Delhi", latitude=28.5410, longitude=77.2830),
        models.Hospital(name="Max Super Speciality Hospital", city="Delhi", latitude=28.5700, longitude=77.2400),
        models.Hospital(name="Safdarjung Hospital", city="Delhi", latitude=28.5675, longitude=77.2050),
        models.Hospital(name="BLK Max Hospital", city="Delhi", latitude=28.6448, longitude=77.1897),
        models.Hospital(name="Medanta Hospital", city="Gurgaon", latitude=28.4395, longitude=77.0400),
        models.Hospital(name="Artemis Hospital", city="Gurgaon", latitude=28.4500, longitude=77.0850),
        models.Hospital(name="Paras Hospital", city="Gurgaon", latitude=28.4210, longitude=77.0405),
        models.Hospital(name="Columbia Asia Hospital", city="Gurgaon", latitude=28.4560, longitude=77.0720),
    ]

    # Insert only new hospitals
    for hospital in new_hospitals:
        if hospital.name not in existing_names:
            db.add(hospital)

    db.commit()

    hospitals = db.query(models.Hospital).all()

    # Add services if not exist
    for h in hospitals:
        existing_services = db.query(models.Service).filter(
            models.Service.hospital_id == h.hospital_id
        ).all()

        if not existing_services:
            services = [
                models.Service(hospital_id=h.hospital_id, service_name="blood test", price=400 + h.hospital_id * 50),
                models.Service(hospital_id=h.hospital_id, service_name="x ray", price=700 + h.hospital_id * 60),
                models.Service(hospital_id=h.hospital_id, service_name="mri", price=2500 + h.hospital_id * 100),
                models.Service(hospital_id=h.hospital_id, service_name="ct scan", price=2000 + h.hospital_id * 90),
            ]
            db.add_all(services)

    db.commit()

    # Add doctors if not exist
    for h in hospitals:
        doctor_exists = db.query(models.Doctor).filter(
            models.Doctor.hospital_id == h.hospital_id
        ).first()

        if not doctor_exists:
            doctor = models.Doctor(
                name=f"Dr. {h.name.split()[0]}",
                hospital_id=h.hospital_id,
                fee=500 + h.hospital_id * 50
            )
            db.add(doctor)
            db.commit()
            db.refresh(doctor)

            slots = [
                models.DoctorSlot(doctor_id=doctor.doctor_id, slot_time=datetime(2026, 4, 1, 10, 0), is_booked=False),
                models.DoctorSlot(doctor_id=doctor.doctor_id, slot_time=datetime(2026, 4, 1, 12, 0), is_booked=False),
                models.DoctorSlot(doctor_id=doctor.doctor_id, slot_time=datetime(2026, 4, 2, 11, 0), is_booked=False),
            ]
            db.add_all(slots)
            db.commit()

    return {"message": "Database seeded/updated successfully"}