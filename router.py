from fastapi import APIRouter
from repository import CountryRepository
from schemas import SCountry, SCountryAdd, SCountryId
from typing import List

router = APIRouter(
    prefix="/countries",
    tags=["Countries"],
)

@router.post("")
async def add_country(name: str, official_language: str, population: int, area: float, gdp: float) -> SCountryId:
    country = SCountryAdd(name=name, official_language=official_language, population=population, area=area, gdp=gdp)
    new_country_id = await CountryRepository.add_country(country)
    new_id = SCountryId(id=new_country_id)
    return new_id

@router.get("")
async def get_countries() -> List[SCountry]:
    countries = await CountryRepository.get_countries()
    return countries