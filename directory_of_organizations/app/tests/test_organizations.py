import uuid
from httpx import AsyncClient
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.organization import Organization


# Проверяем получение организаций
async def test_get_organizations_list(
    async_client: AsyncClient, auth_headers: dict, async_organization_orm: Organization
):
    response = await async_client.get("/organizations/", headers=auth_headers)
    assert response.status_code == 200
    orgs = response.json()
    assert any(str(async_organization_orm.id) == o["id"] for o in orgs)


# Проверяем получение организаций по ID здания
async def test_get_organizations_by_activity(
    async_client: AsyncClient, auth_headers: dict, async_organization_orm: Organization
):
    response = await async_client.get(
        f"/organizations/by-activity/{async_organization_orm.activities[0].id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    orgs = response.json()
    assert any(str(async_organization_orm.id) == o["id"] for o in orgs)


# Проверяем получение организаций по ID здания
async def test_get_organizations_by_building(
    async_client: AsyncClient,
    auth_headers: dict,
    async_building_orm: Organization,
    async_organization_orm: Organization, # Как минимум 1 организация уже будет
    async_db: AsyncSession
):
    response = await async_client.get(
        f"/organizations/by-building/{async_building_orm.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    orgs = response.json()
    response_ids = {uuid.UUID(o["id"]) for o in orgs}

    result = await async_db.execute(select(Organization).filter(Organization.building_id == async_building_orm.id))
    orgs_in_db = result.scalars().all()
    db_ids = {org.id for org in orgs_in_db}

    assert db_ids.issubset(response_ids)

# Проверяем поиск организаций в радиусе 1 км от здания тестовой организации
async def test_get_organizations_by_radius(
    async_client: AsyncClient, auth_headers: dict, async_organization_orm: Organization
):
    # Точка около "ул. Пушкина, д.1"
    latitude = async_organization_orm.building.latitude
    longitude = async_organization_orm.building.longitude
    radius_km = 1.0

    response = await async_client.get(
        f"/organizations/by-radius/?latitude={latitude}&longitude={longitude}&radius_km={radius_km}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    orgs = response.json()
    assert any(str(async_organization_orm.id) == o["id"] for o in orgs)


# Проверяем поиск организаций по части имени
async def test_search_organizations_by_name(
    async_client: AsyncClient, auth_headers: dict, async_organization_orm: Organization
):
    name = async_organization_orm.name
    partial_name = name[: len(name) // 2]
    response = await async_client.get(
        f"/organizations/?name={partial_name}", headers=auth_headers
    )
    assert response.status_code == 200
    orgs = response.json()
    assert any(str(async_organization_orm.id) == o["id"] for o in orgs)


# Проверяем получение организации по ID
async def test_get_organizations_by_id(
    async_client: AsyncClient, auth_headers: dict, async_organization_orm: Organization
):
    response = await async_client.get(
        f"/organizations/{async_organization_orm.id}", headers=auth_headers
    )
    assert response.status_code == 200
    org = response.json()
    assert str(async_organization_orm.id) == org["id"]


# Проверяем создание организации
async def test_create_organization(
    async_client: AsyncClient,
    auth_headers: dict,
    async_activity_orm: Organization,
    async_building_orm: Organization,
    async_db: AsyncSession,
):
    payload = {
        "name": "New Organization",
        "activity_ids": [str(async_activity_orm.id)],
        "building_id": str(async_building_orm.id),
    }
    response = await async_client.post(
        "/organizations/", headers=auth_headers, json=payload
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]

    result = await async_db.execute(select(Organization).filter(Organization.id == uuid.UUID(data["id"])))
    org_in_db = result.scalars().first()
    assert org_in_db is not None
    assert org_in_db.name == payload["name"]