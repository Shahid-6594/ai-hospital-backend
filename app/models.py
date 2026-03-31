from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    hospital_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(Text)
    city = Column(String)
    phone = Column(String)
    latitude = Column(String)
    longitude = Column(String)


class Service(Base):
    __tablename__ = "services"

    service_id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"))
    service_name = Column(String)
    price = Column(Integer)
    duration_minutes = Column(Integer)


class Department(Base):
    __tablename__ = "departments"

    department_id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"))
    name = Column(String)


class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"))
    department_id = Column(Integer, ForeignKey("departments.department_id"))
    name = Column(String)
    experience = Column(Integer)
    consultation_fee = Column(Integer)


class DoctorSlot(Base):
    __tablename__ = "doctor_slots"

    slot_id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"))
    slot_time = Column(TIMESTAMP)
    is_booked = Column(Boolean)


class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    phone = Column(String)
    email = Column(String)
    password_hash = Column(String)


class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"))
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"))
    slot_id = Column(Integer, ForeignKey("doctor_slots.slot_id"))
    booking_time = Column(TIMESTAMP)


class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.hospital_id"))
    patient_id = Column(Integer, ForeignKey("patients.patient_id"))
    rating = Column(Integer)
    comment = Column(Text)