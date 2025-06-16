from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()


# Чтобы фронт (если будет с другого порта) мог обращаться
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # на проде сузить список
    allow_methods=["*"],
    allow_headers=["*"],
)

# Раздаём статичные файлы (html, js, css)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    content = {"message": "Привет, Настя! FastAPI работает."}
    return JSONResponse(content=content, media_type="application/json; charset=utf-8")

# Пример простого расписания на неделю (по дням)
@app.get("/api/schedule")
async def get_schedule():
    return {
        "2025-06-16": ["11:00", "12:00", "14:00"],
        "2025-06-17": ["10:00", "11:00", "15:00"],
        "2025-06-18": ["10:00", "11:00", "13:00"],
        # дальше добавь реальные даты из БД
    }