"""Activity repository"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    """Activity repository"""

    def __init__(self, db: AsyncSession):
        super().__init__(Activity, db)

    async def get_by_deal(self, deal_id: int, limit: int = 100) -> list[Activity]:
        """Get activities for a deal"""
        query = (
            select(Activity)
            .where(Activity.deal_id == deal_id)
            .order_by(Activity.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

