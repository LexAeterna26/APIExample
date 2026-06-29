from pydantic import BaseModel, ConfigDict

class SCountryAdd(BaseModel):
    name: str
    official_language: str
    population: int
    area: float
    gdp: float

class SCountry(SCountryAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SCountryId(BaseModel):
    id: int