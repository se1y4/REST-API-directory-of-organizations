from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import BaseModel
from .organization import Organization


class OrganizationPhone(BaseModel):
    __tablename__ = "organization_phones"

    phone: Mapped[str] = mapped_column(String, nullable=False)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False
    )

    organization: Mapped["Organization"] = relationship(
        back_populates="phones", lazy="selectin"
    )