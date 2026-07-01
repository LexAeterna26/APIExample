from fastapi import APIRouter, HTTPException, status, Depends
from repository import CountryRepository
from schemas import SCountry, SCountryAdd, SCountryUpdate, NotFoundMessage, CountriesStats, SortOptions
from typing import List
from sqlalchemy.exc import NoResultFound

router = APIRouter(
    prefix="/countries",
    tags=["Countries"],
)

@router.post("")
async def add_country(country: SCountryAdd = Depends()) -> SCountry:
    new_country_id = await CountryRepository.add_country(country)
    new_country = await CountryRepository.get_country(new_country_id)
    return new_country

@router.get("")
async def get_countries(sort: SortOptions = Depends()) -> List[SCountry]:
    countries = await CountryRepository.get_countries(sort)
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
async def update_country(country_id: int, country: SCountryUpdate = Depends()) -> SCountry:
    try:
        updated_country_id = await CountryRepository.update_country(country_id, country)
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
