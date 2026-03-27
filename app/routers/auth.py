from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import SessionLocal
from app import models
from app.utils.auth import hash_password, verify_password
from app.utils.jwt_handler import create_access_token

router = APIRouter()

# DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request Models
class RegisterRequest(BaseModel):
    name: str
    age: int
    gender: str
    phone: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register_patient(data: RegisterRequest, db: Session = Depends(get_db)):
    hashed = hash_password(data.password)

    patient = models.Patient(
        name=data.name,
        age=data.age,
        gender=data.gender,
        phone=data.phone,
        email=data.email,
        password_hash=hashed
    )

    db.add(patient)
    db.commit()

    return {"message": "Patient registered successfully"}


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(
        models.Patient.email == data.email
    ).first()

    if not patient:
        return {"error": "User not found"}

    if not verify_password(data.password, patient.password_hash):
        return {"error": "Invalid password"}

    token = create_access_token({"patient_id": patient.patient_id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }