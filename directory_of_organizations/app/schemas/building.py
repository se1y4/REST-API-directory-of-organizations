import uuid
from pydantic import BaseModel, Field


class BuildingBase(BaseModel):
    address: str = Field(..., min_length=1, max_length=255)
    latitude: float
    longitude: float


class BuildingCreate(BuildingBase):
    pass


class BuildingRead(BuildingBase):
    id: uuid.UUID

    model_config = {"from_attributes": True}