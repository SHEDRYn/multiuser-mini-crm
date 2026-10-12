"""Permission checks service"""

from app.core.exceptions import ForbiddenException
from app.models.organization_member import MemberRole, OrganizationMember


class PermissionService:
    """Service for checking user permissions"""

    @staticmethod
    def can_manage_organization(membership: OrganizationMember) -> bool:
        """Check if user can manage organization settings"""
        return membership.role in [MemberRole.OWNER, MemberRole.ADMIN]

    @staticmethod
    def can_manage_all_resources(membership: OrganizationMember) -> bool:
        """Check if user can manage all resources in organization"""
        return membership.role in [MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MANAGER]

    @staticmethod
    def can_rollback_stage(membership: OrganizationMember) -> bool:
        """Check if user can rollback deal stage"""
        return membership.role in [MemberRole.OWNER, MemberRole.ADMIN]

    @staticmethod
    def is_member_role(membership: OrganizationMember) -> bool:
        """Check if user has member role (lowest privileges)"""
        return membership.role == MemberRole.MEMBER

    @staticmethod
    def check_resource_ownership(
        membership: OrganizationMember, resource_owner_id: int
    ) -> None:
        """Check if user can modify resource (for members - only their own)"""
        if PermissionService.can_manage_all_resources(membership):
            return

        if membership.user_id != resource_owner_id:
            raise ForbiddenException("You can only modify your own resources")

    @staticmethod
    def can_view_resource(membership: OrganizationMember) -> bool:
        """Check if user can view resources (all roles can view)"""
        return True

