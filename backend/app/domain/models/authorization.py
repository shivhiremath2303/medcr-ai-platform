from enum import Enum, StrEnum
from typing import Any, Dict, List, Set

from app.domain.models.user import UserRole


class Permission(StrEnum):
    # Document Permissions
    DOC_READ = "document:read"
    DOC_UPLOAD = "document:upload"
    DOC_DELETE = "document:delete"
    DOC_DOWNLOAD = "document:download"

    # Chat Permissions
    CHAT_ASK = "chat:ask"
    CHAT_HISTORY = "chat:history"
    CHAT_DELETE = "chat:delete"

    # Analysis Permissions
    ANALYSIS_RUN = "analysis:run"
    ANALYSIS_EXPORT = "analysis:export"

    # Admin Permissions
    ADMIN_SYSTEM_HEALTH = "admin:system_health"
    ADMIN_METRICS = "admin:metrics"
    ADMIN_USER_MANAGE = "admin:user_manage"
    ADMIN_CACHE_MANAGE = "admin:cache_manage"


class Role(StrEnum):
    """Legacy Role model for backward compatibility with existing tests."""

    ADMIN = "admin"
    LAWYER = "lawyer"
    PARALEGAL = "paralegal"
    REVIEWER = "reviewer"
    READ_ONLY = "read_only"


class RolePermissions:
    """Helper for checking permissions (used by tests)."""

    @staticmethod
    def get_for_role(role: Any) -> Set[Permission]:
        return ROLE_PERMISSIONS.get(role, set())


# Role to Permission Mapping
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.ADMIN: set(Permission),  # Admins have all permissions
    UserRole.LAWYER: {
        Permission.DOC_READ,
        Permission.DOC_UPLOAD,
        Permission.DOC_DOWNLOAD,
        Permission.CHAT_ASK,
        Permission.CHAT_HISTORY,
        Permission.CHAT_DELETE,
        Permission.ANALYSIS_RUN,
        Permission.ANALYSIS_EXPORT,
        Permission.ADMIN_SYSTEM_HEALTH,
    },
    UserRole.PARALEGAL: {
        Permission.DOC_READ,
        Permission.DOC_UPLOAD,
        Permission.CHAT_ASK,
        Permission.CHAT_HISTORY,
        Permission.ANALYSIS_RUN,
    },
    UserRole.REVIEWER: {
        Permission.DOC_READ,
        Permission.CHAT_ASK,
        Permission.CHAT_HISTORY,
    },
    UserRole.READ_ONLY: {
        Permission.DOC_READ,
        Permission.CHAT_HISTORY,
    },
}
