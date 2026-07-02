from contextlib import asynccontextmanager
from database import create_tables
from fastapi import FastAPI
from router import router as countries_router


# Создание таблицы в базе данных
@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_tables()
    print("Database is ready")
    yield


# Создание экземпляра приложения
app = FastAPI(lifespan=lifespan)
app.include_router(countries_router)
