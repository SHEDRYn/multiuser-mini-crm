"""Deal schemas"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.deal import DealStage, DealStatus


class DealBase(BaseModel):
    """Deal base schema"""

    title: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    currency: str = Field("USD", min_length=3, max_length=3)
    status: DealStatus = DealStatus.NEW
    stage: DealStage = DealStage.QUALIFICATION


class DealCreate(BaseModel):
    """Deal create schema"""

    contact_id: int
    title: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(0, ge=0, decimal_places=2)
    currency: str = Field("USD", min_length=3, max_length=3)


class DealUpdate(BaseModel):
    """Deal update schema"""

    title: str | None = Field(None, min_length=1, max_length=255)
    amount: Decimal | None = Field(None, ge=0, decimal_places=2)
    currency: str | None = Field(None, min_length=3, max_length=3)
    status: DealStatus | None = None
    stage: DealStage | None = None
    contact_id: int | None = None


class DealResponse(BaseModel):
    """Deal response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    contact_id: int
    owner_id: int
    title: str
    amount: Decimal
    currency: str
    status: str
    stage: str
    created_at: datetime
    updated_at: datetime


class DealListParams(BaseModel):
    """Deal list query parameters"""

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    status: list[DealStatus] | None = None
    stage: DealStage | None = None
    min_amount: Decimal | None = Field(None, ge=0)
    max_amount: Decimal | None = Field(None, ge=0)
    owner_id: int | None = None
    order_by: str = "created_at"
    order: str = "desc"

