"""Test permissions service"""

import pytest

from app.core.exceptions import ForbiddenException
from app.models.organization_member import MemberRole, OrganizationMember
from app.services.permissions import PermissionService


def create_membership(role: MemberRole, user_id: int = 1) -> OrganizationMember:
    """Helper to create membership object"""
    return OrganizationMember(
        id=1, organization_id=1, user_id=user_id, role=role.value
    )


@pytest.mark.unit
class TestPermissionService:
    """Test permission service"""

    def test_owner_can_manage_organization(self):
        """Test that owner can manage organization"""
        membership = create_membership(MemberRole.OWNER)
        assert PermissionService.can_manage_organization(membership) is True

    def test_admin_can_manage_organization(self):
        """Test that admin can manage organization"""
        membership = create_membership(MemberRole.ADMIN)
        assert PermissionService.can_manage_organization(membership) is True

    def test_manager_cannot_manage_organization(self):
        """Test that manager cannot manage organization"""
        membership = create_membership(MemberRole.MANAGER)
        assert PermissionService.can_manage_organization(membership) is False

    def test_member_cannot_manage_organization(self):
        """Test that member cannot manage organization"""
        membership = create_membership(MemberRole.MEMBER)
        assert PermissionService.can_manage_organization(membership) is False

    def test_manager_can_manage_all_resources(self):
        """Test that manager can manage all resources"""
        membership = create_membership(MemberRole.MANAGER)
        assert PermissionService.can_manage_all_resources(membership) is True

    def test_member_cannot_manage_all_resources(self):
        """Test that member cannot manage all resources"""
        membership = create_membership(MemberRole.MEMBER)
        assert PermissionService.can_manage_all_resources(membership) is False

    def test_member_can_access_own_resource(self):
        """Test that member can access their own resource"""
        membership = create_membership(MemberRole.MEMBER, user_id=1)
        # Should not raise exception
        PermissionService.check_resource_ownership(membership, resource_owner_id=1)

    def test_member_cannot_access_others_resource(self):
        """Test that member cannot access other's resource"""
        membership = create_membership(MemberRole.MEMBER, user_id=1)
        with pytest.raises(ForbiddenException):
            PermissionService.check_resource_ownership(membership, resource_owner_id=2)

    def test_manager_can_access_any_resource(self):
        """Test that manager can access any resource"""
        membership = create_membership(MemberRole.MANAGER, user_id=1)
        # Should not raise exception
        PermissionService.check_resource_ownership(membership, resource_owner_id=999)

    def test_admin_can_rollback_stage(self):
        """Test that admin can rollback deal stage"""
        membership = create_membership(MemberRole.ADMIN)
        assert PermissionService.can_rollback_stage(membership) is True

    def test_manager_cannot_rollback_stage(self):
        """Test that manager cannot rollback deal stage"""
        membership = create_membership(MemberRole.MANAGER)
        assert PermissionService.can_rollback_stage(membership) is False

