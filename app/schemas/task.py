"""Task schemas"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskBase(BaseModel):
    """Task base schema"""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    due_date: date | None = None

    @field_validator("due_date")
    def validate_due_date(cls, v: date | None) -> date | None:
        """Validate that due_date is not in the past"""
        if v is not None and v < date.today():
            raise ValueError("due_date cannot be in the past")
        return v


class TaskCreate(TaskBase):
    """Task create schema"""

    deal_id: int


class TaskUpdate(BaseModel):
    """Task update schema"""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    due_date: date | None = None
    is_done: bool | None = None

    @field_validator("due_date")
    def validate_due_date(cls, v: date | None) -> date | None:
        """Validate that due_date is not in the past"""
        if v is not None and v < date.today():
            raise ValueError("due_date cannot be in the past")
        return v


class TaskResponse(BaseModel):
    """Task response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    deal_id: int
    title: str
    description: str | None
    due_date: date | None
    is_done: bool
    created_at: datetime


class TaskListParams(BaseModel):
    """Task list query parameters"""

    deal_id: int | None = None
    only_open: bool = False
    due_before: date | None = None
    due_after: date | None = None

