# app/main.py

from fastapi import FastAPI, APIRouter, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.infrastructure.logger import logger
from app.infrastructure.exception_handler import global_exception_handler
from app.infrastructure.init_db import init_db
from app.api.main import api_router

# Собираем все наши маршруты
main_router = APIRouter()
main_router.include_router(api_router)

app = FastAPI(
    title="EasyTravel API",
    description="Бэкенд для приложения EasyTravel",
    version="1.0.0",
)

# Подключаем CORS, чтобы фронтенд мог обращаться к бэку
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # фронтенд на этом адресе
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрируем маршруты под префиксом /api
app.include_router(main_router, prefix="/api")

# Перехватчик ошибок
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, global_exception_handler)
app.add_exception_handler(RequestValidationError, global_exception_handler)

# Middleware для логирования каждого запроса
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("➡️  %s %s", request.method, request.url)
    response = await call_next(request)
    logger.info("⬅️  %s %s", response.status_code, request.url)
    return response



# При старте инициализируем БД
@app.on_event("startup")
async def on_startup():
    await init_db()

# Точка входа, если запускаем напрямую
if __name__ == "__main__":
    # Для локальной разработки:
    uvicorn.run("app.main:app", host="127.0.0.1", port=5000, reload=True)
    # В Docker-контейнере:
    # uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
