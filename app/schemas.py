from pydantic import BaseModel
from datetime import datetime


class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    phone: str
    email: str
    password: str


class PatientLogin(BaseModel):
    email: str
    password: str


class AppointmentCreate(BaseModel):
    doctor_id: int
    slot_id: int


class AppointmentResponse(BaseModel):
    appointment_id: int
    doctor: str
    hospital: str
    slot_time: datetime


class ServiceSearch(BaseModel):
    name: str


class ServiceSearchResponse(BaseModel):
    hospital: str
    service: str
    price: int
    city: str


# ---------- Nearby Search ----------

class NearbySearch(BaseModel):
    name: str
    user_lat: float
    user_lon: float


class NearbySearchResponse(BaseModel):
    hospital: str
    service: str
    price: int
    city: str
    distance_km: float