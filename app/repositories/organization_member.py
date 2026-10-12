"""Organization Member repository"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization_member import OrganizationMember
from app.repositories.base import BaseRepository


class OrganizationMemberRepository(BaseRepository[OrganizationMember]):
    """Organization Member repository"""

    def __init__(self, db: AsyncSession):
        super().__init__(OrganizationMember, db)

    async def get_membership(
        self, organization_id: int, user_id: int
    ) -> OrganizationMember | None:
        """Get membership by organization and user"""
        result = await self.db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_organization_members(self, organization_id: int) -> list[OrganizationMember]:
        """Get all members of an organization"""
        result = await self.db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id
            )
        )
        return list(result.scalars().all())

