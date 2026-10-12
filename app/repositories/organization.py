"""Organization repository"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.organization import Organization
from app.models.organization_member import OrganizationMember
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """Organization repository"""

    def __init__(self, db: AsyncSession):
        super().__init__(Organization, db)

    async def get_user_organizations(self, user_id: int) -> list[Organization]:
        """Get all organizations where user is a member"""
        result = await self.db.execute(
            select(Organization)
            .join(OrganizationMember)
            .where(OrganizationMember.user_id == user_id)
        )
        return list(result.scalars().all())

