from sqlalchemy import select
from database import CountryOrm, new_session
from schemas import SCountryAdd, SCountry, SCountryUpdate
from typing import List

class CountryRepository:
    @classmethod
    async def add_country(cls, country: SCountryAdd) -> int:
        async with new_session() as session:
            data = country.model_dump()
            new_country = CountryOrm(**data)
            session.add(new_country)
            await session.flush()
            await session.commit()
            return new_country.id

    @classmethod
    async def get_countries(cls) -> List[SCountry]:
        async with new_session() as session:
            query = select(CountryOrm)
            result = await session.execute(query)
            country_models = result.scalars().all()
            countries = [SCountry.model_validate(country_model) for country_model in country_models]
            return countries

    @classmethod
    async def get_country(cls, country_id: int) -> SCountry:
        async with new_session() as session:
            query = select(CountryOrm).where(CountryOrm.id == country_id)
            result = await session.execute(query)
            country_model = result.scalar_one()
            country = SCountry.model_validate(country_model)
            return country

    @classmethod
    async def update_country(cls, country: SCountryUpdate) -> int:
        async with new_session() as session:
            query = select(CountryOrm).where(CountryOrm.id == country.id)
            result = await session.execute(query)
            country_model = result.scalar_one()
            for key, value in country.model_dump(exclude_none=True).items():
                setattr(country_model, key, value)
            await session.commit()
            return country.id

    @classmethod
    async def delete_country(cls, country_id: int):
        async with new_session() as session:
            query = select(CountryOrm).where(CountryOrm.id == country_id)
            result = await session.execute(query)
            country_model = result.scalar_one()
            await session.delete(country_model)
            await session.commit()
            return
