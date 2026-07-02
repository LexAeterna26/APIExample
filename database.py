from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Создание асинхронного подключения и фабрики сессий
engine = create_async_engine("sqlite+aiosqlite:///countries.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)


# Родительский класс для модели
class Model(DeclarativeBase):
    pass


# Модель для описания таблицы countries в базе данных
class CountryOrm(Model):
    __tablename__ = "countries"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    official_language: Mapped[str]
    population: Mapped[int]
    area: Mapped[float]
    gdp: Mapped[float]


# Функция для создания таблицы в базе данных
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)
