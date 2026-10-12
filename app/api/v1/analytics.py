"""Analytics endpoints"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_membership, get_organization_id
from app.db.session import get_db
from app.models.organization_member import OrganizationMember
from app.schemas.analytics import DealsFunnel, DealsSummary
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get("/deals/summary", response_model=DealsSummary)
async def get_deals_summary(
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DealsSummary:
    """
    Get deals summary analytics for current organization.

    Includes:
    - Total deals count
    - Deals count by status
    - Total amount by status
    - Average won deal amount
    - New deals in last 30 days
    """
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_deals_summary(organization_id)


@router.get("/deals/funnel", response_model=DealsFunnel)
async def get_deals_funnel(
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DealsFunnel:
    """
    Get deals funnel analytics for current organization.

    Shows:
    - Deals count per stage
    - Status breakdown per stage
    - Conversion rates between stages
    """
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_deals_funnel(organization_id)

