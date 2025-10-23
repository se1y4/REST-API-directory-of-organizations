from sqlalchemy import Column, ForeignKey, Table

from app.models.base import Base


# --- многие ко многим Organization & Activity ---
organization_activities = Table(
    "organization_activities",
    Base.metadata,
    Column("organization_id", ForeignKey("organizations.id"), primary_key=True),
    Column("activity_id", ForeignKey("activities.id"), primary_key=True),
)