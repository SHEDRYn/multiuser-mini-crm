"""Organization endpoints"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.organization import OrganizationMemberResponse
from app.services.organization import OrganizationService

router = APIRouter()


@router.get("/me", response_model=list[OrganizationMemberResponse])
async def get_my_organizations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[OrganizationMemberResponse]:
    """
    Get list of organizations where current user is a member.

    Returns organization details along with user's role in each organization.
    """
    org_service = OrganizationService(db)
    organizations = await org_service.get_user_organizations(current_user.id)

    # Get memberships
    result = []
    for org in organizations:
        membership = await org_service.get_user_membership(org.id, current_user.id)
        result.append(
            OrganizationMemberResponse(
                id=membership.id,
                organization=org,
                role=membership.role,
            )
        )

    return result

