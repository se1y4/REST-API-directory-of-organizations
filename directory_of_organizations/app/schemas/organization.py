import uuid
from pydantic import BaseModel, Field

from .activity import ActivityRead
from .building import BuildingRead
from .phone import OrganizationPhoneCreate, OrganizationPhoneRead


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)


class OrganizationCreate(OrganizationBase):
    building_id: uuid.UUID
    phone_numbers: list[OrganizationPhoneCreate] = []
    activity_ids: list[uuid.UUID] = []


class OrganizationRead(OrganizationBase):
    id: uuid.UUID
    building: BuildingRead
    phones: list[OrganizationPhoneRead] = []
    activities: list[ActivityRead] = []

    model_config = {"from_attributes": True}