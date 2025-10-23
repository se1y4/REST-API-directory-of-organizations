from typing import List
from sqlalchemy import String, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import BaseModel
from .organization import Organization

class Building(BaseModel):
    __tablename__ = "buildings"

    address: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    organizations: Mapped[List["Organization"]] = relationship(
        back_populates="building", lazy="selectin"
    )