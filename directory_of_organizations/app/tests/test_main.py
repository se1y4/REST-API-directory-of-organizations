from httpx import AsyncClient
import pytest


pytestmark = pytest.mark.asyncio


# Проверяем, что без токена доступ запрещён (ожидаем 401 Unauthorized)
async def test_access_without_token(async_client: AsyncClient):
    print(async_client.base_url)
    response = await async_client.get("/organizations/")
    print(response.headers)
    assert response.status_code == 401


# Проверяем доступ с токеном (200 или 404, если организаций нет)
async def test_access_with_token(
    async_client: AsyncClient,
    auth_headers: dict,
):
    response = await async_client.get("/organizations/", headers=auth_headers)
    assert response.status_code in (200, 404)