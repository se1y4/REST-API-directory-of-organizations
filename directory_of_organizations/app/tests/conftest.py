import asyncio
import os
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload
import pytest

os.environ["CONFIG_PATH"] = "/../../config_test.yaml"
from app.main import app
from app.api.deps import get_async_db
from app.models.building import Building 
from app.models.organization import Organization 
from app.models.activity import Activity
from app.models.base import BaseModel
from app.core.config import settings


# Переопределяем зависимость get_async_db для использования тестовой базы данных
@pytest.fixture(autouse=True)
def override_get_async_db(async_db_engine):
    async_session = async_sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_db_engine,
        class_=AsyncSession,
    )

    async def _get_test_session():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_async_db] = _get_test_session
    yield
    app.dependency_overrides.clear()


# Создаём и удаляем тестовую базу данных перед/после каждого теста
@pytest.fixture(scope="function")
async def async_db_engine():
    async_engine = create_async_engine(
        url=str(settings.MAIN_DATABASE_URI),
        echo=True,
    )

    async with async_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield async_engine

    async with async_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


# Создаём сессию для тестовой базы и очищаем таблицы после каждого теста
@pytest.fixture(scope="function")
async def async_db(async_db_engine):
    async_session = async_sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_db_engine,
        class_=AsyncSession,
    )

    async with async_session() as session:
        await session.begin()

        yield session

        await session.rollback()

        for table in reversed(BaseModel.metadata.sorted_tables):
            await session.execute(text(f"TRUNCATE {table.name} CASCADE;"))
            await session.commit()


# Асинхронный HTTP-клиент для тестирования API
@pytest.fixture(scope="session")
async def async_client() -> AsyncClient:
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url=f"http://localhost{settings.service.API_PREFIX}",
    )


# Создаём отдельный цикл событий для тестов
@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# Заголовки с токеном авторизации для тестов
@pytest.fixture
async def auth_headers():
    return {"X-API-Token": settings.security.API_TOKEN}


# Фикстура для создания тестового здания
@pytest.fixture
async def async_building_orm(async_db: AsyncSession) -> Building:
    building = Building(address="test", latitude=55.751244, longitude=37.618423)
    async_db.add(building)
    await async_db.commit()
    await async_db.refresh(building)
    return building


# Фикстура для создания тестовой активности
@pytest.fixture
async def async_activity_orm(async_db: AsyncSession) -> Activity:
    activity = Activity(name="test")
    async_db.add(activity)
    await async_db.commit()
    await async_db.refresh(activity)
    return activity


# Фикстура для создания тестовой организации с привязанным зданием и активностью
@pytest.fixture
async def async_organization_orm(
    async_db: AsyncSession, async_building_orm: Building, async_activity_orm: Activity
) -> Organization:
    organization = Organization(
        name="Полуфабрикаты и Молочка",
        building_id=async_building_orm.id,
    )
    organization.activities.extend([async_activity_orm])
    async_db.add(organization)
    await async_db.commit()

    # Reload with building and activities preloaded
    result = await async_db.execute(
        select(Organization)
        .options(
            selectinload(Organization.building), selectinload(Organization.activities)
        )
        .where(Organization.id == organization.id)
    )
    return result.scalar_one()