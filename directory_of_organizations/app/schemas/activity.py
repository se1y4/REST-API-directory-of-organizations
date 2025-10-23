import uuid
from pydantic import BaseModel, Field


class ActivityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class ActivityCreate(ActivityBase):
    parent_id: uuid.UUID | None = None


class ActivityRead(ActivityBase):
    id: uuid.UUID

    model_config = {"from_attributes": True}