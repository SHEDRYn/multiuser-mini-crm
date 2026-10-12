"""Organization service"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.repositories.organization import OrganizationRepository
from app.repositories.organization_member import OrganizationMemberRepository
from app.services.permissions import PermissionService


class OrganizationService:
    """Organization service"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.org_repo = OrganizationRepository(db)
        self.member_repo = OrganizationMemberRepository(db)

    async def get_user_organizations(self, user_id: int) -> list[Organization]:
        """Get all organizations where user is a member"""
        return await self.org_repo.get_user_organizations(user_id)

    async def get_user_membership(
        self, organization_id: int, user_id: int
    ) -> OrganizationMember:
        """Get user membership in organization"""
        membership = await self.member_repo.get_membership(organization_id, user_id)
        if not membership:
            raise NotFoundException("You are not a member of this organization")
        return membership

    async def check_access(self, organization_id: int, user_id: int) -> OrganizationMember:
        """Check if user has access to organization"""
        return await self.get_user_membership(organization_id, user_id)

