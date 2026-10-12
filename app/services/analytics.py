"""Analytics service"""

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import DealStage
from app.repositories.deal import DealRepository
from app.schemas.analytics import DealsFunnel, DealsSummary, FunnelStageStats


class AnalyticsService:
    """Analytics service"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.deal_repo = DealRepository(db)

    async def get_deals_summary(self, organization_id: int) -> DealsSummary:
        """Get deals summary analytics"""
        summary_data = await self.deal_repo.get_summary(organization_id, days=30)

        return DealsSummary(
            total_deals=sum(summary_data["deals_by_status"].values()),
            deals_by_status=summary_data["deals_by_status"],
            amount_by_status=summary_data["amount_by_status"],
            average_won_amount=summary_data["average_won_amount"],
            new_deals_last_30_days=summary_data["new_deals_last_n_days"],
        )

    async def get_deals_funnel(self, organization_id: int) -> DealsFunnel:
        """Get deals funnel analytics"""
        funnel_data = await self.deal_repo.get_funnel(organization_id)

        stages = []
        previous_total = None

        for stage_data in funnel_data:
            # Calculate conversion rate from previous stage
            conversion_rate = None
            if previous_total and previous_total > 0:
                conversion_rate = (stage_data["total"] / previous_total) * 100

            stages.append(
                FunnelStageStats(
                    stage=stage_data["stage"],
                    total=stage_data["total"],
                    by_status=stage_data["by_status"],
                    conversion_rate=conversion_rate,
                )
            )
            previous_total = stage_data["total"]

        return DealsFunnel(stages=stages)

