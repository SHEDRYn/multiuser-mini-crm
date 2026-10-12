"""Authentication service"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.organization_member import MemberRole
from app.models.user import User
from app.repositories.organization import OrganizationRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.repositories.user import UserRepository
from app.schemas.auth import Token, UserRegister


class AuthService:
    """Authentication service"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.org_repo = OrganizationRepository(db)
        self.member_repo = OrganizationMemberRepository(db)

    async def register(self, user_data: UserRegister) -> Token:
        """Register new user and create their first organization"""
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise ConflictException("User with this email already exists")

        # Create user
        user = await self.user_repo.create(
            {
                "email": user_data.email,
                "hashed_password": get_password_hash(user_data.password),
                "name": user_data.name,
            }
        )

        # Create organization
        organization = await self.org_repo.create({"name": user_data.organization_name})

        # Add user as owner of organization
        await self.member_repo.create(
            {
                "organization_id": organization.id,
                "user_id": user.id,
                "role": MemberRole.OWNER,
            }
        )

        await self.db.commit()

        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return Token(access_token=access_token, refresh_token=refresh_token)

    async def login(self, email: str, password: str) -> Token:
        """Login user and return tokens"""
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Incorrect email or password")

        # Generate tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return Token(access_token=access_token, refresh_token=refresh_token)

    async def get_current_user(self, user_id: int) -> User:
        """Get current user by ID"""
        user = await self.user_repo.get(user_id)
        if not user:
            raise UnauthorizedException("User not found")
        return user

