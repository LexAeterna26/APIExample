from sqlalchemy import select
from database import CountryOrm, new_session
from schemas import SCountryAdd, SCountry
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