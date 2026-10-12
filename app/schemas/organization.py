"""Organization schemas"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrganizationBase(BaseModel):
    """Organization base schema"""

    name: str = Field(..., min_length=1, max_length=255)


class OrganizationCreate(OrganizationBase):
    """Organization create schema"""

    pass


class OrganizationUpdate(BaseModel):
    """Organization update schema"""

    name: str | None = Field(None, min_length=1, max_length=255)


class OrganizationResponse(OrganizationBase):
    """Organization response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class OrganizationMemberResponse(BaseModel):
    """Organization member response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    organization: OrganizationResponse
    role: str

