"""API dependencies"""

from typing import Annotated

from fastapi import Depends, Header
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.db.session import get_db
from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.services.auth import AuthService
from app.services.organization import OrganizationService


async def get_token_from_header(authorization: str = Header(...)) -> str:
    """Extract token from Authorization header"""
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise UnauthorizedException("Invalid authentication scheme")
        return token
    except ValueError:
        raise UnauthorizedException("Invalid authorization header")


async def get_current_user(
    token: Annotated[str, Depends(get_token_from_header)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Get current authenticated user"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = int(payload.get("sub"))
        token_type: str = payload.get("type")

        if token_type != "access":
            raise UnauthorizedException("Invalid token type")

    except (JWTError, ValueError, TypeError):
        raise UnauthorizedException("Could not validate credentials")

    auth_service = AuthService(db)
    user = await auth_service.get_current_user(user_id)
    return user


async def get_organization_id(x_organization_id: int = Header(..., alias="X-Organization-Id")) -> int:
    """Get organization ID from header"""
    return x_organization_id


async def get_current_membership(
    current_user: Annotated[User, Depends(get_current_user)],
    organization_id: Annotated[int, Depends(get_organization_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrganizationMember:
    """Get current user's membership in the organization"""
    org_service = OrganizationService(db)
    membership = await org_service.get_user_membership(organization_id, current_user.id)
    return membership

