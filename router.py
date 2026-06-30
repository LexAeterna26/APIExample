from fastapi import APIRouter, HTTPException, status
from starlette.responses import JSONResponse

from repository import CountryRepository
from schemas import SCountry, SCountryAdd, SCountryId, NotFoundMessage
from typing import List, Union
from sqlalchemy.exc import NoResultFound

router = APIRouter(
    prefix="/countries",
    tags=["Countries"],
)

@router.post("")
async def add_country(
        name: str,
        official_language: str,
        population: int,
        area: float,
        gdp: float,
) -> SCountryId:
    country = SCountryAdd(
        name=name,
        official_language=official_language,
        population=population,
        area=area,
        gdp=gdp,
    )
    new_country_id = await CountryRepository.add_country(country)
    new_id = SCountryId(id=new_country_id)
    return new_id

@router.get("")
async def get_countries() -> List[SCountry]:
    countries = await CountryRepository.get_countries()
    return countries

@router.get("/{country_id}",
            responses={404: {"model": NotFoundMessage}})
async def get_country(country_id: int) -> Union[SCountry, None]:
    try:
        country = await CountryRepository.get_country(country_id)
        return country
    except NoResultFound:
        return JSONResponse(
            status_code=404,
            content={"detail": f"There is no country with ID {country_id}"},
        )
