"""Authentication schemas"""

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """User registration schema"""

    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=255)
    organization_name: str = Field(..., min_length=1, max_length=255)


class UserLogin(BaseModel):
    """User login schema"""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response schema"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema"""

    sub: int
    exp: int
    type: str

