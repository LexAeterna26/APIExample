import asyncio
import database
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


# Фикстура для подмены движка для тестов
# Позволяет не затрагивать рабочую базу данных
@pytest.fixture(scope="session")
def engine():
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    database.engine = test_engine
    database.new_session = async_sessionmaker(test_engine, expire_on_commit=False)
    yield test_engine

    asyncio.run(test_engine.dispose())


# Фикстура для очистки таблицы после каждого теста
@pytest.fixture(autouse=True)
def clean_table(engine):
    yield

    async def clear():
        async with database.new_session() as session:
            await session.execute(text("DELETE FROM countries"))
            await session.commit()
    asyncio.run(clear())


# Фикстура для создания тестового клиента
@pytest.fixture
def test_client(engine):
    from main import app

    with TestClient(app) as client:
        yield client


# Тест на успешное добавление страны
def test_add_country_success(test_client):
    payload = {
        "name": "France",
        "official_language": "French",
        "population": 67390000,
        "area": 551695,
        "gdp": 2937000000000,
    }
    response = test_client.post("/countries", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] > 0
    assert data["name"] == payload["name"]


# Тест на валидацию числового поля при добавлении страны
def test_add_country_validation_error(test_client):
    payload = {
        "name": "Invalid",
        "official_language": "Invalid",
        "population": -100,
        "area": 100,
        "gdp": 100,
    }
    response = test_client.post("/countries", json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(err["loc"] == ["body", "population"] for err in errors)


# Тест на валидацию отсутствующего поля при добавлении страны
def test_add_country_missing_field(test_client):
    payload = {
        "name": "Missing field",
        "official_language": "English",
        "population": 1000000,
        "area": 1000,
        # gdp отсутствует
    }
    response = test_client.post("/countries", json=payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(err["loc"] == ["body", "gdp"] for err in errors)


# Тест на получения списка стран при пустой базе данных
def test_get_countries_empty(test_client):
    response = test_client.get("/countries")
    assert response.status_code == 200
    assert response.json() == []


# Тест на получение списка стран, когда база данных не пуста
def test_get_countries_with_data(test_client):
    country1 = {
        "name": "Germany",
        "official_language": "German",
        "population": 83100000,
        "area": 357022,
        "gdp": 4260000000000,
    }
    country2 = {
        "name": "Italy",
        "official_language": "Italian",
        "population": 60360000,
        "area": 301340,
        "gdp": 2100000000000,
    }
    test_client.post("/countries", json=country1)
    test_client.post("/countries", json=country2)

    response = test_client.get("/countries")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = [c["name"] for c in data]
    assert "Germany" in names
    assert "Italy" in names


# Тест на получение списка стран отсортированных по имени в алфавитном порядке
def test_get_countries_sort_by_name_asc(test_client):
    countries = [
        {
            "name": "Zambia",
            "official_language": "English",
            "population": 100,
            "area": 10,
            "gdp": 100,
        },
        {
            "name": "Austria",
            "official_language": "German",
            "population": 200,
            "area": 20,
            "gdp": 200,
        },
        {
            "name": "Brazil",
            "official_language": "Portuguese",
            "population": 300,
            "area": 30,
            "gdp": 300,
        },
    ]
    for c in countries:
        test_client.post("/countries", json=c)

    response = test_client.get("/countries?sort_by=name&order=asc")
    assert response.status_code == 200
    data = response.json()
    names = [c["name"] for c in data]
    assert names == sorted(names)


# Тест на получение списка стран отсортированных по имени в обратном порядке
def test_get_countries_sort_by_name_desc(test_client):
    countries = [
        {
            "name": "Zambia",
            "official_language": "English",
            "population": 100,
            "area": 10,
            "gdp": 100,
        },
        {
            "name": "Austria",
            "official_language": "German",
            "population": 200,
            "area": 20,
            "gdp": 200,
        },
        {
            "name": "Brazil",
            "official_language": "Portuguese",
            "population": 300,
            "area": 30,
            "gdp": 300,
        },
    ]
    for c in countries:
        test_client.post("/countries", json=c)

    response = test_client.get("/countries?sort_by=name&order=desc")
    assert response.status_code == 200
    data = response.json()
    names = [c["name"] for c in data]
    assert names == sorted(names, reverse=True)


# Тест на получение статистики, когда база данных пуста
def test_get_stats_empty(test_client):
    response = test_client.get("/countries/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["population"]["min"] is None
    assert data["population"]["max"] is None
    assert data["population"]["avg"] is None
    assert data["area"]["min"] is None
    assert data["area"]["max"] is None
    assert data["area"]["avg"] is None
    assert data["gdp"]["min"] is None
    assert data["gdp"]["max"] is None
    assert data["gdp"]["avg"] is None


# Тест на получение статистики
def test_get_stats_with_data(test_client):
    countries = [
        {
            "name": "A",
            "official_language": "A",
            "population": 10,
            "area": 1.0,
            "gdp": 100.0,
        },
        {
            "name": "B",
            "official_language": "B",
            "population": 20,
            "area": 2.0,
            "gdp": 200.0,
        },
        {
            "name": "C",
            "official_language": "C",
            "population": 30,
            "area": 3.0,
            "gdp": 300.0,
        },
    ]
    for c in countries:
        test_client.post("/countries", json=c)

    response = test_client.get("/countries/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["population"]["min"] == 10
    assert data["population"]["max"] == 30
    assert data["population"]["avg"] == 20
    assert data["area"]["min"] == 1.0
    assert data["area"]["max"] == 3.0
    assert data["area"]["avg"] == 2.0
    assert data["gdp"]["min"] == 100.0
    assert data["gdp"]["max"] == 300.0
    assert data["gdp"]["avg"] == 200.0


# Тест на получение информации о стране
def test_get_country_success(test_client):
    payload = {
        "name": "Spain",
        "official_language": "Spanish",
        "population": 47350000,
        "area": 505990,
        "gdp": 1420000000000,
    }
    create_resp = test_client.post("/countries", json=payload)
    country_id = create_resp.json()["id"]

    response = test_client.get(f"/countries/{country_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == country_id
    assert data["name"] == payload["name"]


# Тест на получение информации о стране, ID которой нет в базе данных
def test_get_country_not_found(test_client):
    non_existent_id = 9999
    response = test_client.get(f"/countries/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"There is no country with ID {non_existent_id}"


# Тест на обновление информации о стране
def test_update_country_success(test_client):
    payload = {
        "name": "UK",
        "official_language": "English",
        "population": 67886000,
        "area": 243610,
        "gdp": 3100000000000,
    }
    create_resp = test_client.post("/countries", json=payload)
    country_id = create_resp.json()["id"]

    update_data = {
        "name": "United Kingdom",
        "official_language": "English",
        "population": 68200000,
        "area": 243610,
        "gdp": 3200000000000,
    }
    response = test_client.put(f"/countries/{country_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == country_id
    assert data["name"] == update_data["name"]
    assert data["population"] == update_data["population"]


# Тест на частичное обновление информации о стране
def test_update_country_partial(test_client):
    payload = {
        "name": "Canada",
        "official_language": "English",
        "population": 38250000,
        "area": 9984670,
        "gdp": 2200000000000,
    }
    create_resp = test_client.post("/countries", json=payload)
    country_id = create_resp.json()["id"]

    update_data = {"population": 39000000, "gdp": 2300000000000}
    response = test_client.put(f"/countries/{country_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["population"] == 39000000
    assert data["gdp"] == 2300000000000
    assert data["name"] == payload["name"]  # не изменилось


# Тест на валидацию числового поля при обновлении информации о стране
def test_update_country_validation_error(test_client):
    payload = {
        "name": "Test",
        "official_language": "Test",
        "population": 100,
        "area": 100,
        "gdp": 100,
    }
    create_resp = test_client.post("/countries", json=payload)
    country_id = create_resp.json()["id"]

    update_data = {"area": -50}
    response = test_client.put(f"/countries/{country_id}", json=update_data)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(err["loc"] == ["body", "area"] for err in errors)


# Тест на обновлении страны, ID которой нет в базе данных
def test_update_country_not_found(test_client):
    non_existent_id = 9999
    update_data = {"name": "NewName"}
    response = test_client.put(f"/countries/{non_existent_id}", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == f"There is no country with ID {non_existent_id}"


# Тест на удаление информации о стране
def test_delete_country_success(test_client):
    payload = {
        "name": "ToDelete",
        "official_language": "Test",
        "population": 100,
        "area": 100,
        "gdp": 100,
    }
    create_resp = test_client.post("/countries", json=payload)
    country_id = create_resp.json()["id"]

    response = test_client.delete(f"/countries/{country_id}")
    assert response.status_code == 204
    # Проверяем, что страна удалена
    get_resp = test_client.get(f"/countries/{country_id}")
    assert get_resp.status_code == 404


# Тест на удаление информации о стране, ID которой нет в базе данных
def test_delete_country_not_found(test_client):
    non_existent_id = 9999
    response = test_client.delete(f"/countries/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"There is no country with ID {non_existent_id}"
