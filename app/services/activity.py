"""Activity service"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.activity import Activity, ActivityType
from app.models.organization_member import OrganizationMember
from app.repositories.activity import ActivityRepository
from app.repositories.deal import DealRepository
from app.schemas.activity import ActivityCreate


class ActivityService:
    """Activity service"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.activity_repo = ActivityRepository(db)
        self.deal_repo = DealRepository(db)

    async def get_activities(
        self, deal_id: int, organization_id: int, membership: OrganizationMember
    ) -> list[Activity]:
        """Get activities for a deal"""
        # Verify deal exists and belongs to organization
        deal = await self.deal_repo.get(deal_id)
        if not deal or deal.organization_id != organization_id:
            raise NotFoundException("Deal not found")

        return await self.activity_repo.get_by_deal(deal_id)

    async def create_comment(
        self,
        deal_id: int,
        data: ActivityCreate,
        organization_id: int,
        membership: OrganizationMember,
    ) -> Activity:
        """Create comment activity"""
        # Verify deal exists and belongs to organization
        deal = await self.deal_repo.get(deal_id)
        if not deal or deal.organization_id != organization_id:
            raise NotFoundException("Deal not found")

        # Only comments can be created via API
        if data.type != ActivityType.COMMENT:
            raise ValueError("Only comments can be created via API")

        activity = await self.activity_repo.create(
            {
                "deal_id": deal_id,
                "author_id": membership.user_id,
                "type": data.type,
                "payload": data.payload,
            }
        )

        await self.db.commit()
        return activity

