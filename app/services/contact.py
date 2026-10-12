"""Contact service"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.models.contact import Contact
from app.models.organization_member import OrganizationMember
from app.repositories.contact import ContactRepository
from app.repositories.deal import DealRepository
from app.schemas.contact import ContactCreate, ContactListParams, ContactUpdate
from app.services.permissions import PermissionService


class ContactService:
    """Contact service"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.contact_repo = ContactRepository(db)
        self.deal_repo = DealRepository(db)

    async def get_contacts(
        self, organization_id: int, params: ContactListParams, membership: OrganizationMember
    ) -> list[Contact]:
        """Get contacts with filters"""
        # Members can filter by their own contacts if owner_id is provided
        owner_id = params.owner_id
        if owner_id and PermissionService.is_member_role(membership):
            if owner_id != membership.user_id:
                raise ForbiddenException("You can only view your own contacts")

        skip = (params.page - 1) * params.page_size
        return await self.contact_repo.get_by_organization(
            organization_id=organization_id,
            skip=skip,
            limit=params.page_size,
            search=params.search,
            owner_id=owner_id,
        )

    async def get_contact(
        self, contact_id: int, organization_id: int, membership: OrganizationMember
    ) -> Contact:
        """Get single contact"""
        contact = await self.contact_repo.get(contact_id)
        if not contact or contact.organization_id != organization_id:
            raise NotFoundException("Contact not found")
        return contact

    async def create_contact(
        self, data: ContactCreate, organization_id: int, user_id: int
    ) -> Contact:
        """Create new contact"""
        contact = await self.contact_repo.create(
            {
                "organization_id": organization_id,
                "owner_id": user_id,
                "name": data.name,
                "email": data.email,
                "phone": data.phone,
            }
        )
        await self.db.commit()
        return contact

    async def update_contact(
        self,
        contact_id: int,
        data: ContactUpdate,
        organization_id: int,
        membership: OrganizationMember,
    ) -> Contact:
        """Update contact"""
        contact = await self.get_contact(contact_id, organization_id, membership)

        # Check permissions
        PermissionService.check_resource_ownership(membership, contact.owner_id)

        update_data = data.model_dump(exclude_unset=True)
        contact = await self.contact_repo.update(contact, update_data)
        await self.db.commit()
        return contact

    async def delete_contact(
        self, contact_id: int, organization_id: int, membership: OrganizationMember
    ) -> None:
        """Delete contact"""
        contact = await self.get_contact(contact_id, organization_id, membership)

        # Check permissions
        PermissionService.check_resource_ownership(membership, contact.owner_id)

        # Check if contact has deals
        deals = await self.deal_repo.get_by_contact(contact_id)
        if deals:
            raise ValidationException("Cannot delete contact with existing deals")

        await self.contact_repo.delete(contact_id)
        await self.db.commit()

