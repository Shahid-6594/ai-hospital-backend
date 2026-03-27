from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth
from app.routers import hospitals
from app.routers import services
from app.routers import appointments
from app.routers import ai_search
from app.routers import map
from app.routers import doctors
from app.database import engine
from app import models

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(doctors.router)
app.include_router(ai_search.router)
app.include_router(auth.router)
app.include_router(hospitals.router)
app.include_router(services.router)
app.include_router(appointments.router)
app.include_router(map.router)

@app.get("/")
def home():
    return {"message": "AI hospital backend is running and database connected"}

models.Base.metadata.create_all(bind=engine)