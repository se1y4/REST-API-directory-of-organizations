from typing import Annotated
import uuid
from pydantic import BaseModel, StringConstraints


class OrganizationPhoneRead(BaseModel):
    id: uuid.UUID
    phone: str

    model_config = {"from_attributes": True}


class OrganizationPhoneCreate(BaseModel):
    phone: Annotated[
        str,
        StringConstraints(pattern=r"(8-\d{3}|\d)-\d{3}-\d{3}(-\d{2}-\d{2})?"),
    ]