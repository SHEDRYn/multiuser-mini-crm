"""Analytics schemas"""

from decimal import Decimal

from pydantic import BaseModel, Field


class DealsSummary(BaseModel):
    """Deals summary analytics schema"""

    total_deals: int
    deals_by_status: dict[str, int]
    amount_by_status: dict[str, Decimal]
    average_won_amount: Decimal
    new_deals_last_30_days: int


class FunnelStageStats(BaseModel):
    """Funnel stage statistics"""

    stage: str
    total: int
    by_status: dict[str, int]
    conversion_rate: float | None = Field(
        None, description="Conversion rate from previous stage in percent"
    )


class DealsFunnel(BaseModel):
    """Deals funnel analytics schema"""

    stages: list[FunnelStageStats]

