"""Pytest configuration and fixtures"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Organization, OrganizationMember, User
from app.models.organization_member import MemberRole

# Test database URL (use separate test database)
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/crm_db", "/crm_test_db")

# Create async engine for tests
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_maker = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Create test database and session"""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with test_session_maker() as session:
        yield session

    # Drop all tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with overridden database dependency"""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    """Create test user"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        name="Test User",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def test_organization(db: AsyncSession) -> Organization:
    """Create test organization"""
    org = Organization(name="Test Organization")
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@pytest.fixture
async def test_membership(
    db: AsyncSession, test_user: User, test_organization: Organization
) -> OrganizationMember:
    """Create test organization membership"""
    membership = OrganizationMember(
        organization_id=test_organization.id,
        user_id=test_user.id,
        role=MemberRole.OWNER,
    )
    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return membership


@pytest.fixture
def auth_headers(test_user: User) -> dict[str, str]:
    """Get authorization headers for test user"""
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def org_headers(test_organization: Organization) -> dict[str, str]:
    """Get organization headers"""
    return {"X-Organization-Id": str(test_organization.id)}


@pytest.fixture
def full_headers(auth_headers: dict[str, str], org_headers: dict[str, str]) -> dict[str, str]:
    """Get full headers (auth + organization)"""
    return {**auth_headers, **org_headers}

