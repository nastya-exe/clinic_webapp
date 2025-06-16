from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from db import database
import uvicorn
from dotenv import load_dotenv
import os
load_dotenv()

from config import DATABASE_URL

app = FastAPI()

# CORS для фронтенда, если нужен
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В проде — сузить
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Пример расписания — в реале брать из БД!
SCHEDULE = {
    "2025-06-16": ["11:00", "12:00", "14:00"],
    "2025-06-17": ["10:00", "11:00", "15:00"],
    "2025-06-18": ["10:00", "11:00", "13:00"],
}

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
async def get_schedule():
    # Возвращаем даты с доступным временем (без занятых слотов)
    result = {}
    for date, times in SCHEDULE.items():
        free_times = [t for t in times if BOOKINGS.get(date, {}).get(t) is None]
        result[date] = free_times
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

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
