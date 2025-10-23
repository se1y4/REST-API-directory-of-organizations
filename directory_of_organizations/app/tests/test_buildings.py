import uuid
from httpx import AsyncClient
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.building import Building


# Проверяем получение зданий
async def test_get_buildings_list(
    async_client: AsyncClient, auth_headers: dict, async_building_orm: Building
):
    response = await async_client.get("/buildings/", headers=auth_headers)
    assert response.status_code == 200
    orgs = response.json()
    assert any(str(async_building_orm.id) == o["id"] for o in orgs)


# Проверяем получение здания по ID
async def test_get_buildings_by_id(
    async_client: AsyncClient, auth_headers: dict, async_building_orm: Building
):
    response = await async_client.get(
        f"/buildings/{async_building_orm.id}", headers=auth_headers
    )
    assert response.status_code == 200
    org = response.json()
    assert str(async_building_orm.id) == org["id"]


# Проверяем создание здания
async def test_create_building(
    async_client: AsyncClient,
    auth_headers: dict,
    async_db: AsyncSession,
):
    payload = {
        "address": "ул. Пушкина, д. 44",
        "latitude": 54.2233,
        "longitude": 75.573
    }
    response = await async_client.post(
        "/buildings/", headers=auth_headers, json=payload
    )
    assert response.status_code == 201
    data = response.json()
    assert data["address"] == payload["address"]

    result = await async_db.execute(select(Building).filter(Building.id == uuid.UUID(data["id"])))
    org_in_db = result.scalars().first()
    assert org_in_db is not None
    assert org_in_db.address == payload["address"]