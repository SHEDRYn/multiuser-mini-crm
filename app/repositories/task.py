"""Task repository"""

from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Task repository"""

    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)

    async def get_by_deal(
        self,
        deal_id: int,
        only_open: bool = False,
        due_before: date | None = None,
        due_after: date | None = None,
    ) -> list[Task]:
        """Get tasks by deal with filters"""
        query = select(Task).where(Task.deal_id == deal_id)

        if only_open:
            query = query.where(Task.is_done == False)

        if due_before:
            query = query.where(Task.due_date <= due_before)

        if due_after:
            query = query.where(Task.due_date >= due_after)

        query = query.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_organization_tasks(
        self,
        organization_id: int,
        only_open: bool = False,
        due_before: date | None = None,
        due_after: date | None = None,
    ) -> list[Task]:
        """Get all tasks for an organization"""
        from app.models.deal import Deal

        query = (
            select(Task).join(Deal).where(Deal.organization_id == organization_id)
        )

        if only_open:
            query = query.where(Task.is_done == False)

        if due_before:
            query = query.where(Task.due_date <= due_before)

        if due_after:
            query = query.where(Task.due_date >= due_after)

        query = query.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

