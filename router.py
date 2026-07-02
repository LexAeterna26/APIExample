from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from repository import CountryRepository
from schemas import (
    CountriesStats,
    NotFoundMessage,
    SCountry,
    SCountryAdd,
    SCountryUpdate,
    SortOptions,
)
from sqlalchemy.exc import NoResultFound

# Объявление роутера
router = APIRouter(
    prefix="/countries",
    tags=["Countries"],
)


# Эндпоинт для добавления новой страны
@router.post("")
async def add_country(country: SCountryAdd) -> SCountry:
    new_country_id = await CountryRepository.add_country(country)
    new_country = await CountryRepository.get_country(new_country_id)
    return new_country


# Эндпоинт для получения данных о всех странах
@router.get("")
async def get_countries(sort: SortOptions = Depends()) -> List[SCountry]:
    countries = await CountryRepository.get_countries(sort)
    return countries


# Эндпоинт для получения статистики по всем странам
@router.get("/stats")
async def get_stats() -> CountriesStats:
    stats = await CountryRepository.get_stats()
    return stats


# Эндпоинт для получения данных о стране
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


# Эндпоинт для изменения данных о стране
@router.put(
    "/{country_id}",
    response_model=SCountry,
    responses={404: {"model": NotFoundMessage}},
)
async def update_country(country_id: int, country: SCountryUpdate) -> SCountry:
    try:
        updated_country_id = await CountryRepository.update_country(country_id, country)
        updated_country = await CountryRepository.get_country(updated_country_id)
        return updated_country
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no country with ID {country_id}",
        )


# Эндпоинт для удаления данных о стране
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
