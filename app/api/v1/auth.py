"""Authentication endpoints"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import Token, UserLogin, UserRegister
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=Token, status_code=201)
async def register(
    user_data: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    Register a new user and create their first organization.

    The user will be assigned as the owner of the created organization.
    """
    auth_service = AuthService(db)
    return await auth_service.register(user_data)


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    Login with email and password.

    Returns access and refresh JWT tokens.
    """
    auth_service = AuthService(db)
    return await auth_service.login(credentials.email, credentials.password)

