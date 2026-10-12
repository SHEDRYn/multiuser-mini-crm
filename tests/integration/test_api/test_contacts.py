"""Test contacts API"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Contact, OrganizationMember


@pytest.mark.integration
class TestContactsAPI:
    """Test contacts endpoints"""

    async def test_create_contact(
        self, client: AsyncClient, full_headers: dict, test_membership: OrganizationMember
    ):
        """Test creating a contact"""
        response = await client.post(
            "/api/v1/contacts",
            headers=full_headers,
            json={
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["email"] == "john.doe@example.com"
        assert "id" in data

    async def test_get_contacts(
        self,
        client: AsyncClient,
        full_headers: dict,
        test_membership: OrganizationMember,
        db: AsyncSession,
    ):
        """Test getting list of contacts"""
        # Create a contact
        contact = Contact(
            organization_id=test_membership.organization_id,
            owner_id=test_membership.user_id,
            name="Test Contact",
            email="test@example.com",
        )
        db.add(contact)
        await db.commit()

        response = await client.get("/api/v1/contacts", headers=full_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    async def test_get_contact_by_id(
        self,
        client: AsyncClient,
        full_headers: dict,
        test_membership: OrganizationMember,
        db: AsyncSession,
    ):
        """Test getting single contact"""
        # Create a contact
        contact = Contact(
            organization_id=test_membership.organization_id,
            owner_id=test_membership.user_id,
            name="Test Contact",
            email="test@example.com",
        )
        db.add(contact)
        await db.commit()
        await db.refresh(contact)

        response = await client.get(f"/api/v1/contacts/{contact.id}", headers=full_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == contact.id
        assert data["name"] == "Test Contact"

    async def test_update_contact(
        self,
        client: AsyncClient,
        full_headers: dict,
        test_membership: OrganizationMember,
        db: AsyncSession,
    ):
        """Test updating a contact"""
        # Create a contact
        contact = Contact(
            organization_id=test_membership.organization_id,
            owner_id=test_membership.user_id,
            name="Old Name",
            email="old@example.com",
        )
        db.add(contact)
        await db.commit()
        await db.refresh(contact)

        response = await client.patch(
            f"/api/v1/contacts/{contact.id}",
            headers=full_headers,
            json={"name": "New Name"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"

    async def test_contact_search(
        self,
        client: AsyncClient,
        full_headers: dict,
        test_membership: OrganizationMember,
        db: AsyncSession,
    ):
        """Test contact search functionality"""
        # Create contacts
        contact1 = Contact(
            organization_id=test_membership.organization_id,
            owner_id=test_membership.user_id,
            name="Alice Smith",
            email="alice@example.com",
        )
        contact2 = Contact(
            organization_id=test_membership.organization_id,
            owner_id=test_membership.user_id,
            name="Bob Jones",
            email="bob@example.com",
        )
        db.add_all([contact1, contact2])
        await db.commit()

        response = await client.get(
            "/api/v1/contacts", headers=full_headers, params={"search": "Alice"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(c["name"] == "Alice Smith" for c in data)

