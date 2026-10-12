"""Contact endpoints"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_membership, get_current_user, get_organization_id
from app.db.session import get_db
from app.models.organization_member import OrganizationMember
from app.models.user import User
from app.schemas.contact import (
    ContactCreate,
    ContactListParams,
    ContactResponse,
    ContactUpdate,
)
from app.services.contact import ContactService

router = APIRouter()


@router.get("", response_model=list[ContactResponse])
async def get_contacts(
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    owner_id: int | None = None,
) -> list[ContactResponse]:
    """
    Get list of contacts with optional filters.

    Filters:
    - page: Page number (starts from 1)
    - page_size: Items per page (max 100)
    - search: Search by name or email
    - owner_id: Filter by contact owner (requires manager/admin/owner role)
    """
    params = ContactListParams(
        page=page, page_size=page_size, search=search, owner_id=owner_id
    )
    contact_service = ContactService(db)
    return await contact_service.get_contacts(organization_id, params, membership)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ContactResponse:
    """Get single contact by ID"""
    contact_service = ContactService(db)
    return await contact_service.get_contact(contact_id, organization_id, membership)


@router.post("", response_model=ContactResponse, status_code=201)
async def create_contact(
    data: ContactCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    organization_id: Annotated[int, Depends(get_organization_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ContactResponse:
    """Create a new contact"""
    contact_service = ContactService(db)
    return await contact_service.create_contact(data, organization_id, current_user.id)


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    data: ContactUpdate,
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ContactResponse:
    """Update a contact (members can only update their own)"""
    contact_service = ContactService(db)
    return await contact_service.update_contact(contact_id, data, organization_id, membership)


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: int,
    organization_id: Annotated[int, Depends(get_organization_id)],
    membership: Annotated[OrganizationMember, Depends(get_current_membership)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a contact (cannot delete if contact has deals)"""
    contact_service = ContactService(db)
    await contact_service.delete_contact(contact_id, organization_id, membership)

