import uuid
from httpx import AsyncClient
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.activity import Activity


# Проверяем получение видов деятельностей
async def test_get_activities_list(
    async_client: AsyncClient, auth_headers: dict, async_activity_orm: Activity
):
    response = await async_client.get("/activities/", headers=auth_headers)
    assert response.status_code == 200
    orgs = response.json()
    assert any(str(async_activity_orm.id) == o["id"] for o in orgs)


# Проверяем получение вида деятельности по ID
async def test_get_activities_by_id(
    async_client: AsyncClient, auth_headers: dict, async_activity_orm: Activity
):
    response = await async_client.get(
        f"/activities/{async_activity_orm.id}", headers=auth_headers
    )
    assert response.status_code == 200
    org = response.json()
    assert str(async_activity_orm.id) == org["id"]


# Проверяем создание вида деятельности
async def test_create_activity(
    async_client: AsyncClient,
    auth_headers: dict,
    async_activity_orm: Activity,
    async_db: AsyncSession,
):
    payload = {
        "name": "New Activity",
        "parent_id": str(async_activity_orm.id),
    }
    response = await async_client.post(
        "/activities/", headers=auth_headers, json=payload
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]

    result = await async_db.execute(select(Activity).filter(Activity.id == uuid.UUID(data["id"])))
    org_in_db = result.scalars().first()
    assert org_in_db is not None
    assert org_in_db.name == payload["name"]