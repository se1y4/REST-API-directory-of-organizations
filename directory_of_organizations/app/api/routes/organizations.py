import uuid
from fastapi import APIRouter, HTTPException, Query, status

from app.crud import organization as org_crud, building as buildings_crud
from app.api.deps import AsyncSessionDep
from app.schemas.organization import OrganizationRead, OrganizationCreate
from app.utils import get_bounding_box_area

router = APIRouter()


@router.post(
    "/",
    response_model=OrganizationRead,
    status_code=status.HTTP_201_CREATED,
    description="Создать новую организацию с указанными данными.",
)
async def create_organization(
    session: AsyncSessionDep,
    organization_in: OrganizationCreate,
):
    """
    Создает новую организацию с указанными данными.
    """
    org = await org_crud.create_organization(
        session,
        name=organization_in.name,
        building_id=organization_in.building_id,
        phone_numbers=[p.phone for p in organization_in.phone_numbers],
        activity_ids=organization_in.activity_ids,
    )
    return org


@router.get(
    "/by-building/{building_id}",
    response_model=list[OrganizationRead],
    description="Получить список организаций, находящихся в указанном здании по его ID.",
)
async def get_organizations_by_building(
    session: AsyncSessionDep,
    building_id: uuid.UUID,
):
    """
    Получает список организаций, находящихся в указанном здании по его ID.
    """
    organizations = await org_crud.get_organizations_by_building(session, building_id)
    if not organizations:
        raise HTTPException(status_code=404, detail="Organizations not found")
    return organizations


@router.get(
    "/by-activity/{activity_id}",
    response_model=list[OrganizationRead],
    description="Получить список организаций по виду деятельности, с возможностью включения дочерних видов.",
)
async def get_organizations_by_activity(
    session: AsyncSessionDep,
    activity_id: uuid.UUID,
    with_children: bool = Query(
        False, description="Включить дочерние виды деятельности"
    ),
):
    """
    Получает список организаций по виду деятельности.
    Если `with_children` равно True, то также включаются организации с дочерними видами деятельности.
    """
    if with_children:
        organizations = await org_crud.get_organizations_by_activity_with_children(
            session,
            root_activity_id=activity_id,
        )
    else:
        organizations = await org_crud.get_organizations_by_activity(
            session, activity_id
        )
    if not organizations:
        raise HTTPException(status_code=404, detail="Organizations not found")
    return organizations


@router.get(
    "/by-radius/",
    response_model=list[OrganizationRead],
    description="Получить список организаций в заданном радиусе (км) от указанной точки (широта и долгота).",
)
async def get_organizations_by_radius(
    session: AsyncSessionDep,
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    radius_km: float = Query(..., gt=0),
):
    """
    Получает список организаций в заданном радиусе от указанной точки (широта и долгота).
    """
    box = get_bounding_box_area(latitude, longitude, radius_km)

    # Находим здания в bounding box
    buildings_in_box = await buildings_crud.get_buildings_by_coordinates(session, box)

    if not buildings_in_box:
        raise HTTPException(status_code=404, detail="No buildings found in radius")

    building_ids = [b.id for b in buildings_in_box]

    # Далее выбираем организации в этих зданиях
    organizations = await org_crud.get_organizations_by_buildings(session, building_ids)
    if not organizations:
        raise HTTPException(status_code=404, detail="No organizations found in radius")
    return organizations


@router.get(
    "/{organization_id}",
    response_model=OrganizationRead,
    description="Получить подробную информацию об организации по её ID.",
)
async def read_organization(
    session: AsyncSessionDep,
    organization_id: uuid.UUID,
):
    """
    Получает подробную информацию об организации по её ID.
    """
    org = await org_crud.get_organization(session, organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.get(
    "/",
    response_model=list[OrganizationRead],
    description="Получить список всех организаций или выполнить поиск по названию, если передан параметр `name`.",
)
async def list_organizations(
    session: AsyncSessionDep,
    name: str | None = None,
):
    """
    Получает список всех организаций
    Если передан параметр `name` - выполняет поиск организаций по названию.
    """
    if name:
        orgs = await org_crud.search_organizations_by_name(session, name)
    else:
        orgs = await org_crud.get_organizations(session)
    return orgs