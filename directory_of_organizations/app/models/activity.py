from typing import List, Optional
import uuid
from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import BaseModel
from .association_tables import organization_activities
from .organization import Organization


class Activity(BaseModel):
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        default=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID, ForeignKey("activity.id"), nullable=True)

    parent: Mapped[Optional["Activity"]] = relationship(
        "Activity", remote_side=[id], back_populates="children", lazy="selectin"
    )
    children: Mapped[List["Activity"]] = relationship(
        "Activity",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    organizations: Mapped[List["Organization"]] = relationship(
        secondary=organization_activities, back_populates="activities", lazy="selectin"
    )