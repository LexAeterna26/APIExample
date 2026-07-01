from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional

class SCountryAdd(BaseModel):
    name: str
    official_language: str
    population: int = Field(ge=0)
    area: float = Field(ge=0.0)
    gdp: float = Field(ge=0.0)

class SCountry(SCountryAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SCountryUpdate(BaseModel):
    name: Optional[str] = None
    official_language: Optional[str] = None
    population: Optional[int] = Field(default=None, ge=0)
    area: Optional[float] = Field(default=None, ge=0.0)
    gdp: Optional[float] = Field(default=None, ge=0.0)

class NotFoundMessage(BaseModel):
    detail: str

class StatsField(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None
    avg: Optional[float] = None

class CountriesStats(BaseModel):
    population: StatsField
    area: StatsField
    gdp: StatsField

class SortOptions(BaseModel):
    sort_by: Optional[str] = None
    order: Optional[str] = "asc"

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, val: Optional[str]) -> Optional[str]:
        allowed = {"name", "official_language", "population", "area", "gdp"}
        if val is not None and val not in allowed:
            raise ValueError(f"Sort_by must be one of {allowed}")
        return val

    @field_validator("order")
    @classmethod
    def validate_order(cls, val: str) -> str:
        if val not in {"asc", "desc"}:
            raise ValueError("Order must be 'asc' or 'desc'")
        return val
