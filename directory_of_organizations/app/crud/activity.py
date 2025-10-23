import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.activity import Activity


# Получить глубину вложенности деятельности
async def get_activity_depth(session: AsyncSession, activity_id: uuid.UUID) -> int:
    depth = 1
    current_id = activity_id

    while True:
        result = await session.execute(
            select(Activity.parent_id).where(Activity.id == current_id)
        )
        parent_id = result.scalar()
        if parent_id is None:
            break
        depth += 1
        current_id = parent_id
        if depth > 3:
            break
    return depth


# Создать деятельность
async def create_activity(
    session: AsyncSession,
    name: str,
    parent_id: uuid.UUID | None = None,
) -> Activity:
    # Проверяем глубину вложенности
    if parent_id is not None:
        depth = await get_activity_depth(session, parent_id)
        if depth >= 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Максимальная глубина вложенности деятельностей — 3 уровня",
            )

    activity = Activity(name=name, parent_id=parent_id)
    session.add(activity)
    await session.commit()
    await session.refresh(activity)
    return activity


# Получить деятельность по id
async def get_activity(
    session: AsyncSession, activity_id: uuid.UUID
) -> Activity | None:
    result = await session.execute(select(Activity).where(Activity.id == activity_id))
    return result.scalar_one_or_none()


# Получить деятельность с дочерними элементами
async def get_activity_with_children(
    session: AsyncSession, activity_id: uuid.UUID
) -> Activity | None:
    result = await session.execute(select(Activity).where(Activity.id == activity_id))
    return result.scalar_one_or_none()


# Получить все деятельности
async def get_activities(session: AsyncSession) -> list[Activity]:
    result = await session.execute(select(Activity))
    return list(result.scalars().all())