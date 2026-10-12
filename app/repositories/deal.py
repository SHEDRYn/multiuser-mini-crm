"""Deal repository"""

from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.repositories.base import BaseRepository


class DealRepository(BaseRepository[Deal]):
    """Deal repository"""

    def __init__(self, db: AsyncSession):
        super().__init__(Deal, db)

    async def get_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
        status: list[str] | None = None,
        stage: str | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
        owner_id: int | None = None,
        order_by: str = "created_at",
        order: str = "desc",
    ) -> list[Deal]:
        """Get deals by organization with filters"""
        query = select(Deal).where(Deal.organization_id == organization_id)

        if status:
            query = query.where(Deal.status.in_(status))

        if stage:
            query = query.where(Deal.stage == stage)

        if min_amount is not None:
            query = query.where(Deal.amount >= min_amount)

        if max_amount is not None:
            query = query.where(Deal.amount <= max_amount)

        if owner_id:
            query = query.where(Deal.owner_id == owner_id)

        # Order by
        order_column = getattr(Deal, order_by, Deal.created_at)
        if order == "asc":
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_contact(self, contact_id: int) -> list[Deal]:
        """Get all deals for a contact"""
        result = await self.db.execute(select(Deal).where(Deal.contact_id == contact_id))
        return list(result.scalars().all())

    async def get_summary(self, organization_id: int, days: int = 30) -> dict:
        """Get deals summary for organization"""
        # Count by status
        status_counts = await self.db.execute(
            select(Deal.status, func.count(Deal.id), func.sum(Deal.amount))
            .where(Deal.organization_id == organization_id)
            .group_by(Deal.status)
        )

        deals_by_status = {}
        amount_by_status = {}
        for status, count, total_amount in status_counts.all():
            deals_by_status[status] = count
            amount_by_status[status] = total_amount or Decimal(0)

        # Average won amount
        avg_won = await self.db.execute(
            select(func.avg(Deal.amount)).where(
                and_(Deal.organization_id == organization_id, Deal.status == "won")
            )
        )
        average_won_amount = avg_won.scalar_one() or Decimal(0)

        # New deals in last N days
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        new_deals = await self.db.execute(
            select(func.count(Deal.id)).where(
                and_(Deal.organization_id == organization_id, Deal.created_at >= cutoff_date)
            )
        )
        new_deals_count = new_deals.scalar_one()

        return {
            "deals_by_status": deals_by_status,
            "amount_by_status": amount_by_status,
            "average_won_amount": average_won_amount,
            "new_deals_last_n_days": new_deals_count,
        }

    async def get_funnel(self, organization_id: int) -> list[dict]:
        """Get deals funnel statistics"""
        result = await self.db.execute(
            select(Deal.stage, Deal.status, func.count(Deal.id))
            .where(Deal.organization_id == organization_id)
            .group_by(Deal.stage, Deal.status)
            .order_by(Deal.stage)
        )

        funnel_data = {}
        for stage, status, count in result.all():
            if stage not in funnel_data:
                funnel_data[stage] = {"stage": stage, "total": 0, "by_status": {}}
            funnel_data[stage]["total"] += count
            funnel_data[stage]["by_status"][status] = count

        return list(funnel_data.values())

