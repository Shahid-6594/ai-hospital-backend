from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.dependencies.auth import get_current_user


router = APIRouter()


@router.get("/doctor-slots/{doctor_id}")
def get_doctor_slots(doctor_id: int, db: Session = Depends(get_db)):

    slots = (
        db.query(models.DoctorSlot)
        .filter(models.DoctorSlot.doctor_id == doctor_id)
        .filter(models.DoctorSlot.is_booked == False)
        .all()
    )

    return slots


@router.post("/book-appointment")
def book_appointment(
    doctor_id: int,
    slot_id: int,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    patient_id = user["patient_id"]

    slot = db.query(models.DoctorSlot).filter(models.DoctorSlot.slot_id == slot_id).first()

    if not slot:
        return {"error": "Slot not found"}

    if slot.is_booked:
        return {"error": "Slot already booked"}

    appointment = models.Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        slot_id=slot_id
    )

    db.add(appointment)

    slot.is_booked = True

    db.commit()

    return {"message": "Appointment booked successfully"}

from app.dependencies.auth import get_current_user


@router.get("/my-appointments")
def my_appointments(user = Depends(get_current_user), db: Session = Depends(get_db)):

    patient_id = user["patient_id"]

    appointments = (
        db.query(
            models.Appointment.appointment_id,
            models.Doctor.name.label("doctor"),
            models.Hospital.name.label("hospital"),
            models.DoctorSlot.slot_time
        )
        .join(models.Doctor, models.Appointment.doctor_id == models.Doctor.doctor_id)
        .join(models.Hospital, models.Doctor.hospital_id == models.Hospital.hospital_id)
        .join(models.DoctorSlot, models.Appointment.slot_id == models.DoctorSlot.slot_id)
        .filter(models.Appointment.patient_id == patient_id)
        .all()
    )

    response = []

    for a in appointments:
        response.append({
            "appointment_id": a.appointment_id,
            "doctor": a.doctor,
            "hospital": a.hospital,
            "slot_time": a.slot_time
        })

    return response

@router.delete("/cancel-appointment/{appointment_id}")
def cancel_appointment(
    appointment_id: int,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    patient_id = user["patient_id"]

    appointment = db.query(models.Appointment).filter(
        models.Appointment.appointment_id == appointment_id
    ).first()

    if not appointment:
        return {"error": "Appointment not found"}

    if appointment.patient_id != patient_id:
        return {"error": "Not authorized"}

    # free the slot again
    slot = db.query(models.DoctorSlot).filter(
        models.DoctorSlot.slot_id == appointment.slot_id
    ).first()

    if slot:
        slot.is_booked = False

    db.delete(appointment)
    db.commit()

    return {"message": "Appointment cancelled"}