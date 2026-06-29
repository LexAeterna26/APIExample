from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_tables
from router import router as countries_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_tables()
    print("Database is ready")
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(countries_router)
