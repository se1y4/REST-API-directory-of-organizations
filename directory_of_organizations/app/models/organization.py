
from typing import List
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.base import BaseModel
from .association_tables import organization_activities
from .building import Building
from .phone import OrganizationPhone
from .activity import Activity


class Organization(BaseModel):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String, nullable=False)
    building_id: Mapped[int] = mapped_column(ForeignKey("buildings.id"), nullable=False)

    building: Mapped["Building"] = relationship(
        back_populates="organizations", lazy="selectin"
    )
    phones: Mapped[List["OrganizationPhone"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan", lazy="selectin"
    )
    activities: Mapped[List["Activity"]] = relationship(
        secondary=organization_activities,
        back_populates="organizations",
        lazy="selectin",
    )