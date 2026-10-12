"""Contact repository"""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.repositories.base import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    """Contact repository"""

    def __init__(self, db: AsyncSession):
        super().__init__(Contact, db)

    async def get_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        owner_id: int | None = None,
    ) -> list[Contact]:
        """Get contacts by organization with filters"""
        query = select(Contact).where(Contact.organization_id == organization_id)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Contact.name.ilike(search_pattern),
                    Contact.email.ilike(search_pattern),
                )
            )

        if owner_id:
            query = query.where(Contact.owner_id == owner_id)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

