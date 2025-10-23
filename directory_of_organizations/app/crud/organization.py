import uuid
from app.models.organization import Organization, OrganizationPhone, Activity
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import literal_column, select
from sqlalchemy.orm import aliased, selectinload


# Создать организацию
async def create_organization(
    session: AsyncSession,
    name: str,
    building_id: uuid.UUID,
    phone_numbers: list[str],
    activity_ids: list[uuid.UUID],
) -> Organization:
    org = Organization(name=name, building_id=building_id)
    # Телефоны
    org.phones = [OrganizationPhone(phone=p) for p in phone_numbers]

    # Активности
    if activity_ids:
        result = await session.execute(
            select(Activity).where(Activity.id.in_(activity_ids))
        )
        activities = result.scalars().all()
        org.activities.extend(activities)

    session.add(org)
    await session.commit()
    await session.refresh(org)
    return org


# Получить организацию по id
async def get_organization(
    session: AsyncSession, organization_id: uuid.UUID
) -> Organization | None:
    result = await session.execute(
        select(Organization).where(Organization.id == organization_id)
    )
    return result.scalar_one_or_none()


# Получить все организации
async def get_organizations(session: AsyncSession) -> list[Organization]:
    result = await session.execute(
        select(Organization).options(
            selectinload(Organization.building),
            selectinload(Organization.activities),
            selectinload(Organization.phones),
        )
    )
    return list(result.scalars().all())


# Получить организации по различным критериям
async def get_organizations_by_building(
    session: AsyncSession, building_id: uuid.UUID
) -> list[Organization]:
    result = await session.execute(
        select(Organization).where(Organization.building_id == building_id)
    )
    return list(result.scalars().all())


# Получить организации по зданиям
async def get_organizations_by_buildings(
    session: AsyncSession, buildings: list[uuid.UUID]
) -> list[Organization]:
    result = await session.execute(
        select(Organization).where(Organization.building_id.in_(buildings))
    )
    return list(result.scalars().all())


# Получить организации по активности
async def get_organizations_by_activity(
    session: AsyncSession, activity_id: uuid.UUID
) -> list[Organization]:
    result = await session.execute(
        select(Organization)
        .join(Organization.activities)
        .where(Activity.id == activity_id)
    )
    return list(result.scalars().all())


# Поиск организаций по имени
async def search_organizations_by_name(
    session: AsyncSession, name_substring: str
) -> list[Organization]:
    result = await session.execute(
        select(Organization).filter(Organization.name.ilike(f"%{name_substring}%"))
    )
    return list(result.scalars().all())


# Получить организации по активности с дочерними элементами
async def get_organizations_by_activity_with_children(
    session: AsyncSession,
    root_activity_id: uuid.UUID,
) -> list[Organization]:
    # Алиасы для таблицы activity
    activity_alias = aliased(Activity)
    activity_cte = (
        select(
            Activity.id,
            Activity.parent_id,
            Activity.name,
            literal_column("1").label("level"),
        )
        .where(Activity.id == root_activity_id)
        .cte(name="activity_cte", recursive=True)
    )

    activity_alias = aliased(Activity, name="a")

    # Рекурсивный запрос для получения всех дочерних активностей
    activity_cte = activity_cte.union_all(
        select(
            activity_alias.id,
            activity_alias.parent_id,
            activity_alias.name,
            (activity_cte.c.level + 1).label("level"),
        ).where(
            (activity_alias.parent_id == activity_cte.c.id) & (activity_cte.c.level < 3)
        )
    )

    # Запрос организаций, которые связаны с активностями из CTE
    query = (
        select(Organization)
        .join(Organization.activities)
        .where(Activity.id.in_(select(activity_cte.c.id)))
        .distinct()
    )

    result = await session.execute(query)
    organizations = list(result.scalars().unique().all())
    return organizations