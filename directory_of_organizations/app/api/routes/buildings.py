from typing import List
import uuid
from fastapi import APIRouter, HTTPException, status

from app.schemas.building import BuildingRead, BuildingCreate
from app.crud import building as building_crud
from app.api.deps import AsyncSessionDep

router = APIRouter()


@router.post("/", response_model=BuildingRead, status_code=status.HTTP_201_CREATED)
async def create_building(
    session: AsyncSessionDep,
    building_in: BuildingCreate,
):
    building = await building_crud.create_building(
        session=session,
        address=building_in.address,
        latitude=building_in.latitude,
        longitude=building_in.longitude,
    )
    return building


@router.get("/{building_id}", response_model=BuildingRead)
async def read_building(
    session: AsyncSessionDep,
    building_id: uuid.UUID,
):
    building = await building_crud.get_building(session, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building


@router.get("/", response_model=List[BuildingRead])
async def list_buildings(
    session: AsyncSessionDep,
):
    buildings = await building_crud.get_buildings(session)
    return buildings