from pydantic import BaseModel, ConfigDict
from typing import Optional

class SCountryAdd(BaseModel):
    name: str
    official_language: str
    population: int
    area: float
    gdp: float

class SCountry(SCountryAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SCountryUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    official_language: Optional[str] = None
    population: Optional[int] = None
    area: Optional[float] = None
    gdp: Optional[float] = None

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
