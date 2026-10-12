"""Contact schemas"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactBase(BaseModel):
    """Contact base schema"""

    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)


class ContactCreate(ContactBase):
    """Contact create schema"""

    pass


class ContactUpdate(BaseModel):
    """Contact update schema"""

    name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)


class ContactResponse(ContactBase):
    """Contact response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    owner_id: int
    created_at: datetime


class ContactListParams(BaseModel):
    """Contact list query parameters"""

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    search: str | None = None
    owner_id: int | None = None

