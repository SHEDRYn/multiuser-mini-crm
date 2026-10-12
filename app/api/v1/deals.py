"""Deal endpoints"""

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_membership, get_current_user, get_organization_id
from app.db.session import get_db
from app.models.deal import DealStage, DealStatus
from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityResponse
from app.schemas.deal import DealCreate, DealListParams, DealResponse, DealUpdate
from app.services.activity import ActivityService
from app.services.deal import DealService

router = APIRouter()


@router.get("", response_model=list[DealResponse])
async def get_deals(
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: list[DealStatus] | None = Query(None),
    stage: DealStage | None = None,
    min_amount: Decimal | None = Query(None, ge=0),
    max_amount: Decimal | None = Query(None, ge=0),
    owner_id: int | None = None,
    order_by: str = "created_at",
    order: str = "desc",
) -> list[DealResponse]:
    """
    Get list of deals with optional filters.

    Filters:
    - page: Page number
    - page_size: Items per page (max 100)
    - status: Filter by status (can specify multiple)
    - stage: Filter by stage
    - min_amount, max_amount: Filter by amount range
    - owner_id: Filter by owner (requires manager/admin/owner role)
    - order_by: Field to sort by
    - order: Sort order (asc/desc)
    """
    params = DealListParams(
        page=page,
        page_size=page_size,
        status=status,
        stage=stage,
        min_amount=min_amount,
        max_amount=max_amount,
        owner_id=owner_id,
        order_by=order_by,
        order=order,
    )
    deal_service = DealService(db)
    return await deal_service.get_deals(organization_id, params, membership)


@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: int,
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DealResponse:
    """Get single deal by ID"""
    deal_service = DealService(db)
    return await deal_service.get_deal(deal_id, organization_id, membership)


@router.post("", response_model=DealResponse, status_code=201)
async def create_deal(
    data: DealCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    organization_id: Annotated[int, Depends(get_organization_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DealResponse:
    """Create a new deal"""
    deal_service = DealService(db)
    return await deal_service.create_deal(data, organization_id, current_user.id)


@router.patch("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: int,
    data: DealUpdate,
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DealResponse:
    """
    Update a deal (members can only update their own).

    Business rules:
    - Cannot close as won if amount <= 0
    - Stage rollback requires admin/owner role
    - Status/stage changes create activities automatically
    """
    deal_service = DealService(db)
    return await deal_service.update_deal(deal_id, data, organization_id, membership)


@router.delete("/{deal_id}", status_code=204)
async def delete_deal(
    deal_id: int,
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a deal"""
    deal_service = DealService(db)
    await deal_service.delete_deal(deal_id, organization_id, membership)


@router.get("/{deal_id}/activities", response_model=list[ActivityResponse])
async def get_deal_activities(
    deal_id: int,
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ActivityResponse]:
    """Get activity timeline for a deal"""
    activity_service = ActivityService(db)
    return await activity_service.get_activities(deal_id, organization_id, membership)


@router.post("/{deal_id}/activities", response_model=ActivityResponse, status_code=201)
async def create_deal_activity(
    deal_id: int,
    data: ActivityCreate,
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ActivityResponse:
    """
    Create a comment activity for a deal.

    Only comments can be created via API.
    Other activity types are created automatically by the system.
    """
    activity_service = ActivityService(db)
    return await activity_service.create_comment(deal_id, data, organization_id, membership)

