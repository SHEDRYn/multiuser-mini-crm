"""Test deals API"""

from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Contact, Deal, OrganizationMember


@pytest.mark.integration
class TestDealsAPI:
    """Test deals endpoints"""

    @pytest.fixture
    async def test_contact(
        self, db: AsyncSession, test_membership: OrganizationMember
    ) -> Contact:
        """Create test contact"""
        contact = Contact(
            organization_id=test_membership.organization_id,
            owner_id=test_membership.user_id,
            name="Test Contact",
            email="contact@example.com",
        )
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact

    async def test_create_deal(
        self,
        client: AsyncClient,
        full_headers: dict,
        test_contact: Contact,
    ):
        """Test creating a deal"""
        response = await client.post(
            "/api/v1/deals",
            headers=full_headers,
            json={
                "contact_id": test_contact.id,
                "title": "Website Redesign",
                "amount": 10000.50,
                "currency": "USD",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Website Redesign"
        assert Decimal(data["amount"]) == Decimal("10000.50")
        assert data["status"] == "new"

    async def test_cannot_close_deal_with_zero_amount(
        self,
        client: AsyncClient,
        full_headers: dict,
        test_contact: Contact,
        test_membership: OrganizationMember,
        db: AsyncSession,
    ):
        """Test that deal with amount 0 cannot be closed as won"""
        # Create deal with amount 0
        deal = Deal(
            organization_id=test_membership.organization_id,
            contact_id=test_contact.id,
            owner_id=test_membership.user_id,
            title="Test Deal",
            amount=Decimal("0"),
            currency="USD",
        )
        db.add(deal)
        await db.commit()
        await db.refresh(deal)

        # Try to close as won
        response = await client.patch(
            f"/api/v1/deals/{deal.id}",
            headers=full_headers,
            json={"status": "won"},
        )

        assert response.status_code == 400
        assert "amount" in response.json()["detail"].lower()

    async def test_get_deals(
        self,
        client: AsyncClient,
        full_headers: dict,
        test_contact: Contact,
        test_membership: OrganizationMember,
        db: AsyncSession,
    ):
        """Test getting list of deals"""
        # Create a deal
        deal = Deal(
            organization_id=test_membership.organization_id,
            contact_id=test_contact.id,
            owner_id=test_membership.user_id,
            title="Test Deal",
            amount=Decimal("5000"),
            currency="USD",
        )
        db.add(deal)
        await db.commit()

        response = await client.get("/api/v1/deals", headers=full_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    async def test_filter_deals_by_status(
        self,
        client: AsyncClient,
        full_headers: dict,
        test_contact: Contact,
        test_membership: OrganizationMember,
        db: AsyncSession,
    ):
        """Test filtering deals by status"""
        # Create deals with different statuses
        deal1 = Deal(
            organization_id=test_membership.organization_id,
            contact_id=test_contact.id,
            owner_id=test_membership.user_id,
            title="New Deal",
            amount=Decimal("1000"),
            currency="USD",
            status="new",
        )
        deal2 = Deal(
            organization_id=test_membership.organization_id,
            contact_id=test_contact.id,
            owner_id=test_membership.user_id,
            title="Won Deal",
            amount=Decimal("5000"),
            currency="USD",
            status="won",
        )
        db.add_all([deal1, deal2])
        await db.commit()

        response = await client.get(
            "/api/v1/deals", headers=full_headers, params={"status": "won"}
        )

        assert response.status_code == 200
        data = response.json()
        assert all(deal["status"] == "won" for deal in data)

