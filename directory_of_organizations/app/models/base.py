from datetime import datetime
import uuid
from sqlalchemy import DateTime, event, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        default=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )


# Автоматическая установка временных меток перед вставкой
@event.listens_for(BaseModel, "before_insert", propagate=True)
def timestamp_before_insert(mapper, connection, target):
    target.created_at = datetime.now()
    target.modified_at = datetime.now()


# Автоматическая установка временных меток перед обновлением
@event.listens_for(BaseModel, "before_update", propagate=True)
def timestamp_before_update(mapper, connection, target):
    target.modified_at = datetime.now()