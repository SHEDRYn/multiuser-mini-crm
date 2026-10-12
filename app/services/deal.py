"""Deal service"""

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.models.activity import ActivityType
from app.models.deal import Deal, DealStage
from app.models.organization_member import OrganizationMember
from app.repositories.activity import ActivityRepository
from app.repositories.contact import ContactRepository
from app.repositories.deal import DealRepository
from app.schemas.deal import DealCreate, DealListParams, DealUpdate
from app.services.permissions import PermissionService


class DealService:
    """Deal service"""

    # Stage order for validation
    STAGE_ORDER = {
        DealStage.QUALIFICATION: 0,
        DealStage.PROPOSAL: 1,
        DealStage.NEGOTIATION: 2,
        DealStage.CLOSED: 3,
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self.deal_repo = DealRepository(db)
        self.contact_repo = ContactRepository(db)
        self.activity_repo = ActivityRepository(db)

    async def get_deals(
        self, organization_id: int, params: DealListParams, membership: OrganizationMember
    ) -> list[Deal]:
        """Get deals with filters"""
        owner_id = params.owner_id
        if owner_id and PermissionService.is_member_role(membership):
            if owner_id != membership.user_id:
                raise ForbiddenException("You can only view your own deals")

        skip = (params.page - 1) * params.page_size
        status_list = [s.value for s in params.status] if params.status else None

        return await self.deal_repo.get_by_organization(
            organization_id=organization_id,
            skip=skip,
            limit=params.page_size,
            status=status_list,
            stage=params.stage.value if params.stage else None,
            min_amount=params.min_amount,
            max_amount=params.max_amount,
            owner_id=owner_id,
            order_by=params.order_by,
            order=params.order,
        )

    async def get_deal(
        self, deal_id: int, organization_id: int, membership: OrganizationMember
    ) -> Deal:
        """Get single deal"""
        deal = await self.deal_repo.get(deal_id)
        if not deal or deal.organization_id != organization_id:
            raise NotFoundException("Deal not found")
        return deal

    async def create_deal(
        self, data: DealCreate, organization_id: int, user_id: int
    ) -> Deal:
        """Create new deal"""
        # Verify contact exists and belongs to organization
        contact = await self.contact_repo.get(data.contact_id)
        if not contact or contact.organization_id != organization_id:
            raise ValidationException("Invalid contact")

        deal = await self.deal_repo.create(
            {
                "organization_id": organization_id,
                "contact_id": data.contact_id,
                "owner_id": user_id,
                "title": data.title,
                "amount": data.amount,
                "currency": data.currency,
            }
        )
        await self.db.commit()
        return deal

    async def update_deal(
        self,
        deal_id: int,
        data: DealUpdate,
        organization_id: int,
        membership: OrganizationMember,
    ) -> Deal:
        """Update deal with business rules validation"""
        deal = await self.get_deal(deal_id, organization_id, membership)

        # Check permissions
        PermissionService.check_resource_ownership(membership, deal.owner_id)

        update_data = data.model_dump(exclude_unset=True)

        # Validate contact if changed
        if "contact_id" in update_data:
            contact = await self.contact_repo.get(update_data["contact_id"])
            if not contact or contact.organization_id != organization_id:
                raise ValidationException("Invalid contact")

        # Business rule: cannot close deal as won if amount <= 0
        if "status" in update_data and update_data["status"] == "won":
            amount = update_data.get("amount", deal.amount)
            if amount <= 0:
                raise ValidationException("Cannot close deal as won with amount <= 0")

        # Business rule: stage rollback
        if "stage" in update_data:
            old_stage_order = self.STAGE_ORDER.get(DealStage(deal.stage), 0)
            new_stage_order = self.STAGE_ORDER.get(DealStage(update_data["stage"]), 0)

            if new_stage_order < old_stage_order:
                if not PermissionService.can_rollback_stage(membership):
                    raise ForbiddenException("Only admin/owner can rollback deal stage")

            # Create activity for stage change
            if update_data["stage"] != deal.stage:
                await self.activity_repo.create(
                    {
                        "deal_id": deal.id,
                        "author_id": membership.user_id,
                        "type": ActivityType.STAGE_CHANGED,
                        "payload": {
                            "old_stage": deal.stage,
                            "new_stage": update_data["stage"],
                        },
                    }
                )

        # Create activity for status change
        if "status" in update_data and update_data["status"] != deal.status:
            await self.activity_repo.create(
                {
                    "deal_id": deal.id,
                    "author_id": membership.user_id,
                    "type": ActivityType.STATUS_CHANGED,
                    "payload": {
                        "old_status": deal.status,
                        "new_status": update_data["status"],
                    },
                }
            )

        deal = await self.deal_repo.update(deal, update_data)
        await self.db.commit()
        return deal

    async def delete_deal(
        self, deal_id: int, organization_id: int, membership: OrganizationMember
    ) -> None:
        """Delete deal"""
        deal = await self.get_deal(deal_id, organization_id, membership)

        # Check permissions
        PermissionService.check_resource_ownership(membership, deal.owner_id)

        await self.deal_repo.delete(deal_id)
        await self.db.commit()

