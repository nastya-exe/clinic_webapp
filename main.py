from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import datetime
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Привет, вебапп работает!"}

# Разрешаем доступ из Telegram WebApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для продакшна укажи точный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модель ответа
class Slot(BaseModel):
    day: str
    start_time: str
    end_time: str

@app.get("/schedule", response_model=List[Slot])
async def get_schedule(doctor_id: int = Query(...)):
    # ВРЕМЕННО: Заглушка, пока без подключения к БД
    sample_schedule = [
        {"day": "Понедельник", "start_time": "09:00", "end_time": "12:00"},
        {"day": "Среда", "start_time": "14:00", "end_time": "17:00"},
        {"day": "Пятница", "start_time": "10:00", "end_time": "13:00"},
    ]
    return sample_schedule
