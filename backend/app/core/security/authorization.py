from typing import Any, Dict, Optional

from app.core.observability.logger import get_logger
from app.domain.models.audit import AuditEventType
from app.domain.models.authorization import ROLE_PERMISSIONS, Permission
from app.domain.models.user import User, UserRole
from app.services.audit.audit_service import AuditService

logger = get_logger(__name__)


class AuthorizationService:
    """
    Evaluates authorization policies for users and resources.
    Implements fine-grained permission checks and resource ownership validation.
    """

    def __init__(self, audit_service: AuditService):
        self.audit_service = audit_service

    def has_permission(self, user: User, permission: Permission) -> bool:
        """
        Check if a user has a specific granular permission based on their role.
        """
        user_permissions = ROLE_PERMISSIONS.get(user.role, set())
        if permission in user_permissions:
            return True

        self.audit_service.log(
            AuditEventType.ACCESS_DENIED,
            action="check_permission",
            status="failure",
            user_id=user.user_id,
            username=user.username,
            details={
                "required_permission": permission,
                "user_role": user.role,
            },
        )
        return False

    def is_resource_owner(
        self, user: User, resource_owner_id: str, admin_bypass: bool = True
    ) -> bool:
        """
        Validate if the current user is the owner of a specific resource.
        """
        if admin_bypass and user.role == UserRole.ADMIN:
            return True

        if user.user_id == resource_owner_id:
            return True

        self.audit_service.log(
            AuditEventType.OWNERSHIP_VIOLATION,
            action="verify_ownership",
            status="failure",
            user_id=user.user_id,
            details={
                "resource_owner_id": resource_owner_id,
            },
        )
        return False

    def can_access_document(
        self, user: User, document_metadata: Dict[str, Any] | None
    ) -> bool:
        """
        Policy-based check for document access.
        """
        if not self.has_permission(user, Permission.DOC_READ):
            return False

        if not document_metadata:
            return True

        owner_id = document_metadata.get("owner_id")
        if owner_id:
            return self.is_resource_owner(user, owner_id)

        return True
