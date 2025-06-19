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
from pydantic import BaseModel
from typing import Optional

load_dotenv()

app = FastAPI() # создание приложения FastAPI, к которому будут цепляться все маршруты

DATABASE_URL = os.getenv("DATABASE_URL")
# CORS — разрешает фронтенду (даже из другого домена)
# делать запросы к API (полезно для WebApp из Telegram).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В проде — сузить
    allow_methods=["*"],
    allow_headers=["*"],
)

#StaticFiles — отдаёт файлы (JS, CSS и т.д.) из папки static/
app.mount("/static", StaticFiles(directory="static"), name="static")

# Храним записи (для примера, в памяти)
BOOKINGS = {}

class BookingRequest(BaseModel):
    date: str
    time: str
    user_name: str

class BookingData(BaseModel):
    doctor_id: int                     # ID врача, к которому записываемся
    appointment_time: datetime         # Время записи (дата + время)
    patient_id: int

# Отдаёт HTML-шаблон на / — это интерфейс WebApp, который открывается в Telegram.
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        content = f.read()
        return HTMLResponse(content=content, media_type="text/html; charset=utf-8")

#Функция для внедрения зависимости Depends(get_session) в каждом маршруте,
# где нужно подключение к базе.
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


# в WebApp для отображения слотов при записи.
@app.get("/api/schedule")
async def get_schedule(
    doctor_id: int = Query(...), # Обязательный параметр doctor_id из query-параметров
    session: AsyncSession = Depends(get_session) # Получаем сессию для работы с БД
):
    # Создаём список дней, за которые будем строить расписание:
    today = datetime.today().date() #Сегодняшняя дата
    days = [today + timedelta(days=i) for i in range(60)]

    result = {}

    # Загружаем расписание врача (рабочие часы по дням)
    stmt = select(DoctorSchedule).where(DoctorSchedule.doctor_id == doctor_id) # Запрашиваем из таблицы DoctorSchedule все строки с рабочими часами врача.
    schedules = (await session.execute(stmt)).scalars().all() # Получаем список объектов DoctorSchedule — каждый с днём недели(day_of_week), временем начала (start_time) и конца (end_time).
    schedule_map = {s.day_of_week.lower(): s for s in schedules} #Превращаем список расписания в словарь по дню недели

    # Загружаем уже занятые записи врача на эти даты
    stmt_bookings = select(Appointments).where(
        Appointments.doctor_id == doctor_id,
        Appointments.appointment_time >= datetime.combine(today, time.min),
        Appointments.appointment_time < datetime.combine(today + timedelta(days=60), time.max)

    )
    bookings = (await session.execute(stmt_bookings)).scalars().all()

    # Создаём множество занятых слотов (для быстрой проверки)
    busy_slots = {
        b.appointment_time.strftime('%Y-%m-%d %H:%M')
        for b in bookings
    }
    # Формируем свободные слоты по дням:
    for day in days:
        dow_en = day.strftime('%A').lower() # День недели, например 'monday'
        if dow_en not in schedule_map:
            continue  # Если врач не работает в этот день — пропускаем

        sched = schedule_map[dow_en]  # Получаем расписание на этот день
        start_time = sched.start_time
        end_time = sched.end_time

        # Генерируем слоты по часу
        current_time = datetime.combine(day, start_time)
        slots = []
        while current_time.time() < end_time:
            slot_str = current_time.strftime('%Y-%m-%d %H:%M')
            # Если слот свободен — добавляем
            if slot_str not in busy_slots:
                slots.append(current_time.strftime('%H:%M'))
            current_time += timedelta(hours=1)

        if slots:
            result[str(day)] = slots

    return result


# Создание записи
@app.post("/api/book")
async def book_appointment(data: BookingData, session: AsyncSession = Depends(get_session)):
    print(f"Получены данные для бронирования: {data}")
    # Формируем запрос, который ищет запись в таблице Appointments с таким же врачом и
    # временем приёма, которое пытаются забронировать.
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
        status=datetime.now(),
        channel='telegram'
    )

    #Добавляем запись в сессию и коммитим изменения — запись сохраняется в бд
    session.add(new_appointment)
    await session.commit()

    print(f"Запись создана: врач {data.doctor_id}, время {data.appointment_time}")

    return {"status": "success"}

# Получает doctor_id и возвращает имя врача.
@app.get("/api/doctor_name")
async def get_doctor_name(doctor_id: int, session: AsyncSession = Depends(get_session)):
    stmt = select(Doctors).where(Doctors.id == doctor_id)
    doctor = (await session.execute(stmt)).scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Врач не найден")
    return {"name": doctor.full_name}


# Просто возвращает список всех врачей из таблицы Doctors.
@app.get("/doctors")
async def get_doctors(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Doctors))
    doctors = result.scalars().all()
    return doctors

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
