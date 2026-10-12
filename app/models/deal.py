"""Deal model"""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DealStatus(str, Enum):
    """Deal status"""

    NEW = "new"
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"


class DealStage(str, Enum):
    """Deal stage in sales funnel"""

    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED = "closed"


class Deal(Base):
    """Deal model"""

    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    contact_id: Mapped[int] = mapped_column(
        ForeignKey("contacts.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=DealStatus.NEW, index=True
    )
    stage: Mapped[str] = mapped_column(
        String(50), nullable=False, default=DealStage.QUALIFICATION, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="deals")
    contact: Mapped["Contact"] = relationship("Contact", back_populates="deals")
    owner: Mapped["User"] = relationship("User", back_populates="owned_deals")
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="deal", cascade="all, delete-orphan"
    )
    activities: Mapped[list["Activity"]] = relationship(
        "Activity", back_populates="deal", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Deal(id={self.id}, title='{self.title}', status='{self.status}')>"

