from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app import models

router = APIRouter()

@router.get("/seed")
def seed_data(db: Session = Depends(get_db)):
    print("SEED FUNCTION CALLED")

    if db.query(models.Hospital).first():
        print("DATA ALREADY EXISTS")
        return {"message": "Database already seeded"}

    print("INSERTING HOSPITALS")

    hospitals_list = [
        models.Hospital(name="AIIMS Delhi", city="Delhi", latitude=28.5672, longitude=77.2100),
        models.Hospital(name="Fortis Hospital", city="Delhi", latitude=28.5670, longitude=77.2420),
    ]

    db.add_all(hospitals_list)
    db.commit()

    print("HOSPITALS INSERTED")

    return {"message": "Seed completed"}