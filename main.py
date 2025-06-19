from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import uvicorn
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, time, timedelta
from db.db_session import async_session
from db.models import DoctorSchedule, Doctors, Appointments
from fastapi import FastAPI, Depends, Query
from dotenv import load_dotenv
import os

from db import models


load_dotenv()

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
# CORS для фронтенда, если нужен
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В проде — сузить
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Храним записи (для примера, в памяти)
BOOKINGS = {}

class BookingRequest(BaseModel):
    date: str
    time: str
    user_name: str

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        content = f.read()
        return HTMLResponse(content=content, media_type="text/html; charset=utf-8")

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


@app.get("/api/schedule")
async def get_schedule(
    doctor_id: int = Query(...),
    session: AsyncSession = Depends(get_session)
):
    today = datetime.today().date()
    days = [today + timedelta(days=i) for i in range(60)]

    result = {}

    # Загружаем расписание врача (рабочие часы по дням)
    stmt = select(DoctorSchedule).where(DoctorSchedule.doctor_id == doctor_id)
    schedules = (await session.execute(stmt)).scalars().all()
    schedule_map = {s.day_of_week.lower(): s for s in schedules}

    # Загружаем уже занятые записи врача на эти даты
    stmt_bookings = select(Appointments).where(
        Appointments.doctor_id == doctor_id,
        Appointments.appointment_time >= datetime.combine(today, time.min),
        Appointments.appointment_time < datetime.combine(today + timedelta(days=60), time.max)

    )
    bookings = (await session.execute(stmt_bookings)).scalars().all()
    busy_slots = {
        b.appointment_time.strftime('%Y-%m-%d %H:%M')
        for b in bookings
    }

    for day in days:
        dow_en = day.strftime('%A').lower()
        if dow_en not in schedule_map:
            continue  # врач не работает в этот день

        sched = schedule_map[dow_en]
        start_time = sched.start_time
        end_time = sched.end_time

        # Генерируем слоты по часу
        current_time = datetime.combine(day, start_time)
        slots = []
        while current_time.time() < end_time:
            slot_str = current_time.strftime('%Y-%m-%d %H:%M')
            # Проверяем, свободен ли слот
            if slot_str not in busy_slots:
                slots.append(current_time.strftime('%H:%M'))
            current_time += timedelta(hours=1)

        if slots:
            result[str(day)] = slots

    return result



@app.post("/api/book")
async def book_appointment(data: BookingData, session: AsyncSession = Depends(get_session)):
    # Проверяем, занят ли слот (через запрос к базе)
    stmt = select(Appointments).where(
        Appointments.doctor_id == data.doctor_id,
        Appointments.appointment_time == data.appointment_time
    )
    existing = await session.execute(stmt)
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Слот уже занят")

    # Создаём запись
    new_appointment = Appointments(
        doctor_id=data.doctor_id,
        appointment_time=data.appointment_time,
        patient_id=data.patient_id,  # или null, если нет
        channel='telegram'
    )
    session.add(new_appointment)
    await session.commit()

    print(f"Запись создана: врач {data.doctor_id}, время {data.appointment_time}")

    return {"status": "success"}


@app.get("/api/doctor_name")
async def get_doctor_name(doctor_id: int, session: AsyncSession = Depends(get_session)):
    stmt = select(Doctors).where(Doctors.id == doctor_id)
    doctor = (await session.execute(stmt)).scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Врач не найден")
    return {"name": doctor.full_name}



@app.get("/doctors")
async def get_doctors(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Doctors))
    doctors = result.scalars().all()
    return doctors

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
