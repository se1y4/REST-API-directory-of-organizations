import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.building import Building
from app.schemas.utils import BoundingBox


# Создать здание
async def create_building(
    session: AsyncSession, address: str, latitude: float, longitude: float
) -> Building:
    building = Building(address=address, latitude=latitude, longitude=longitude)
    session.add(building)

    await session.commit()
    await session.refresh(building)
    return building


# Получить здание по id
async def get_building(
    session: AsyncSession, building_id: uuid.UUID
) -> Building | None:
    result = await session.execute(select(Building).where(Building.id == building_id))
    return result.scalar_one_or_none()


# Получить все здания
async def get_buildings(session: AsyncSession) -> list[Building]:
    result = await session.execute(select(Building))
    return list(result.scalars().all())


# Получить здания по координатам
async def get_buildings_by_coordinates(
    session: AsyncSession, box: BoundingBox
) -> list[Building]:
    result = await session.execute(
        select(Building).where(
            (Building.latitude >= box.min_lat)
            & (Building.latitude <= box.max_lat)
            & (Building.longitude >= box.min_lon)
            & (Building.longitude <= box.max_lon)
        )
    )
    return list(result.scalars().all())