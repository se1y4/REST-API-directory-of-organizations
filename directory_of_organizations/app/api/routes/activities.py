import uuid
from fastapi import APIRouter, HTTPException, status

from app.schemas.activity import ActivityRead, ActivityCreate
from app.crud import activity as activity_crud
from app.api.deps import AsyncSessionDep

router = APIRouter()


@router.post("/", response_model=ActivityRead, status_code=status.HTTP_201_CREATED)
async def create_activity(
    session: AsyncSessionDep,
    activity_in: ActivityCreate,
):
    activity = await activity_crud.create_activity(
        session=session,
        name=activity_in.name,
        parent_id=activity_in.parent_id,
    )
    return activity


@router.get("/{activity_id}", response_model=ActivityRead)
async def read_activity(
    session: AsyncSessionDep,
    activity_id: uuid.UUID,
):
    activity = await activity_crud.get_activity(session, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.get("/", response_model=list[ActivityRead])
async def list_activities(
    session: AsyncSessionDep,
):
    activities = await activity_crud.get_activities(session)
    return activities