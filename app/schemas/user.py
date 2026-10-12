"""User schemas"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    """User base schema"""

    email: EmailStr
    name: str


class UserCreate(UserBase):
    """User create schema"""

    password: str


class UserUpdate(BaseModel):
    """User update schema"""

    name: str | None = None
    email: EmailStr | None = None


class UserResponse(UserBase):
    """User response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime

