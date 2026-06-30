from fastapi import APIRouter, HTTPException, status
from starlette.responses import JSONResponse
from repository import CountryRepository
from schemas import SCountry, SCountryAdd, SCountryUpdate, NotFoundMessage, CountriesStats
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
) -> SCountry:
    country = SCountryAdd(
        name=name,
        official_language=official_language,
        population=population,
        area=area,
        gdp=gdp,
    )
    new_country_id = await CountryRepository.add_country(country)
    country = await CountryRepository.get_country(new_country_id)
    return country

@router.get("")
async def get_countries() -> List[SCountry]:
    countries = await CountryRepository.get_countries()
    return countries

@router.get("/stats")
async def get_stats() -> CountriesStats:
    stats = await CountryRepository.get_stats()
    return stats

@router.get(
    "/{country_id}",
    response_model=SCountry,
    responses={404: {"model": NotFoundMessage}},
)
async def get_country(country_id: int) -> SCountry:
    try:
        country = await CountryRepository.get_country(country_id)
        return country
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no country with ID {country_id}",
        )

@router.put(
    "/{country_id}",
    response_model=SCountry,
    responses={404: {"model": NotFoundMessage}},
)
async def update_country(
        country_id: int,
        name: str = None,
        official_language: str = None,
        population: int = None,
        area: float = None,
        gdp: float = None,
) -> SCountry:
    country = SCountryUpdate(
        id=country_id,
        name=name,
        official_language=official_language,
        population=population,
        area=area,
        gdp=gdp,
    )
    try:
        updated_country_id = await CountryRepository.update_country(country)
        updated_country = await CountryRepository.get_country(updated_country_id)
        return updated_country
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no country with ID {country_id}",
        )

@router.delete(
    "/{country_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": NotFoundMessage}},
)
async def delete_country(country_id: int) -> None:
    try:
        country = await CountryRepository.delete_country(country_id)
        return None
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no country with ID {country_id}",
        )
