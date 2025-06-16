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
from db.models import DoctorSchedule
from fastapi import Depends

from db import models
from db import db_session

load_dotenv()

app = FastAPI()

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
        return f.read()

@app.get("/api/schedule")
async def get_schedule(session: AsyncSession = Depends(get_session)):
    today = datetime.today().date()
    days = [today + timedelta(days=i) for i in range(7)]

    result = {}

    stmt = select(DoctorSchedule)
    schedules = (await session.execute(stmt)).scalars().all()

    for day in days:
        dow = day.strftime('%A').lower()  # 'monday', 'tuesday'...
        for sched in schedules:
            if sched.day_of_week.lower() == dow:
                current = datetime.combine(day, sched.start_time)
                end = datetime.combine(day, sched.end_time)
                slots = []
                while current < end:
                    slots.append(current.strftime('%H:%M'))
                    current += timedelta(minutes=60)  # шаг 1 час
                result.setdefault(str(day), []).extend(slots)

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


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

@app.get("/doctors")
async def get_doctors(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Doctors))
    doctors = result.scalars().all()
    return doctors

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
