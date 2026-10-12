"""Activity model - timeline of deal activities"""

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ActivityType(str, Enum):
    """Activity types"""

    COMMENT = "comment"
    STATUS_CHANGED = "status_changed"
    STAGE_CHANGED = "stage_changed"
    TASK_CREATED = "task_created"
    SYSTEM = "system"


class Activity(Base):
    """Activity model - timeline of events for a deal"""

    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    deal_id: Mapped[int] = mapped_column(
        ForeignKey("deals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    deal: Mapped["Deal"] = relationship("Deal", back_populates="activities")
    author: Mapped["User | None"] = relationship("User", back_populates="activities")

    def __repr__(self) -> str:
        return f"<Activity(id={self.id}, type='{self.type}', deal_id={self.deal_id})>"

