from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import uvicorn
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timedelta, time
from db.db_session import async_session
from db.models import DoctorSchedule, Doctors
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
    days = [today + timedelta(days=i) for i in range(7)]

    result = {}

    # Загружаем расписание врача
    stmt = select(DoctorSchedule).where(DoctorSchedule.doctor_id == doctor_id)
    schedules = (await session.execute(stmt)).scalars().all()
    schedule_map = {s.day_of_week.lower(): s for s in schedules}

    for day in days:
        dow_en = day.strftime('%A').lower()
        if dow_en not in schedule_map:
            continue  # врач не работает в этот день

        sched = schedule_map[dow_en]
        start_time = sched.start_time
        end_time = sched.end_time

        # генерируем слоты по часу
        current_time = datetime.combine(day, start_time)
        slots = []
        while current_time.time() < end_time:
            slots.append(current_time.strftime('%H:%M'))
            current_time += timedelta(hours=1)

        result[str(day)] = slots

    return result



@app.post("/api/book")
async def book_slot(data: BookingRequest):
    # Проверяем свободен ли слот
    if BOOKINGS.get(data.date, {}).get(data.time):
        return {"success": False, "message": "Это время уже занято"}

    # Записываем
    if data.date not in BOOKINGS:
        BOOKINGS[data.date] = {}
    BOOKINGS[data.date][data.time] = data.user_name
    return {"success": True, "message": f"Вы записаны на {data.date} в {data.time}"}



@app.get("/doctors")
async def get_doctors(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Doctors))
    doctors = result.scalars().all()
    return doctors

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
