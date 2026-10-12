"""Activity schemas"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.activity import ActivityType


class ActivityBase(BaseModel):
    """Activity base schema"""

    type: ActivityType
    payload: dict = Field(default_factory=dict)


class ActivityCreate(BaseModel):
    """Activity create schema - only for comments"""

    type: ActivityType = ActivityType.COMMENT
    payload: dict


class ActivityResponse(BaseModel):
    """Activity response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    deal_id: int
    author_id: int | None
    type: str
    payload: dict
    created_at: datetime

