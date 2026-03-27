from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.routers import auth
from app.routers import hospitals
from app.routers import services
from app.routers import appointments
from app.routers import ai_search
from app.routers import map
from app.routers import doctors
from app.routers import seed
from app.routers import debug

from app.database import engine, SessionLocal
from app import models

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(doctors.router)
app.include_router(ai_search.router)
app.include_router(auth.router)
app.include_router(hospitals.router)
app.include_router(services.router)
app.include_router(appointments.router)
app.include_router(map.router)
app.include_router(seed.router)
app.include_router(debug.router)


@app.get("/")
def home():
    return {"message": "AI hospital backend is running and database connected"}


# Create tables + Seed database on startup
@app.on_event("startup")
def startup_event():
    print("Creating tables...")
    models.Base.metadata.create_all(bind=engine)

    print("Seeding database...")
    db = SessionLocal()

    # If data already exists, skip seeding
    if db.query(models.Hospital).first():
        print("Database already seeded")
        db.close()
        return

    # Hospitals
    h1 = models.Hospital(name="City Hospital", city="Delhi", latitude=28.6139, longitude=77.2090)
    h2 = models.Hospital(name="Metro Hospital", city="Delhi", latitude=28.7041, longitude=77.1025)

    db.add_all([h1, h2])
    db.commit()
    db.refresh(h1)
    db.refresh(h2)

    # Services
    services_list = [
        models.Service(hospital_id=h1.hospital_id, service_name="blood test", price=500),
        models.Service(hospital_id=h1.hospital_id, service_name="x ray", price=800),
        models.Service(hospital_id=h2.hospital_id, service_name="mri", price=3000),
        models.Service(hospital_id=h2.hospital_id, service_name="ct scan", price=2500),
    ]
    db.add_all(services_list)
    db.commit()

    # Doctors
    d1 = models.Doctor(name="Dr. Sharma", hospital_id=h1.hospital_id)
    d2 = models.Doctor(name="Dr. Mehta", hospital_id=h2.hospital_id)

    db.add_all([d1, d2])
    db.commit()
    db.refresh(d1)
    db.refresh(d2)

    # Slots
    slots = [
        models.DoctorSlot(doctor_id=d1.doctor_id, slot_time=datetime(2026, 4, 1, 10, 0), is_booked=False),
        models.DoctorSlot(doctor_id=d1.doctor_id, slot_time=datetime(2026, 4, 1, 12, 0), is_booked=False),
        models.DoctorSlot(doctor_id=d2.doctor_id, slot_time=datetime(2026, 4, 2, 11, 0), is_booked=False),
    ]
    db.add_all(slots)
    db.commit()

    db.close()
    print("Database seeded successfully!")