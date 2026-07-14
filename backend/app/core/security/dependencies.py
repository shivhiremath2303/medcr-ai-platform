from dataclasses import dataclass
from typing import List, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from app.core.observability.context import set_user_id
from app.core.observability.logger import get_logger
from app.core.security.auth_service import AuthService
from app.core.security.authorization import AuthorizationService
from app.core.security.jwt import JWTManager
from app.core.security.rate_limiter import RateLimiterService
from app.di import (
    get_audit_service,
    get_auth_service,
    get_authorization_service,
    get_jwt_manager,
    get_rate_limiter_service,
    get_settings_provider,
    get_user_repository,
)
from app.domain.models.audit import AuditEventType
from app.domain.models.authorization import Permission
from app.domain.models.user import User, UserRole
from app.domain.repositories.user_repository import UserRepository
from app.services.audit.audit_service import AuditService

logger = get_logger(__name__)

# auto_error=False allows us to handle the error manually for better logging
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


@dataclass
class CurrentUser:
    """
    CurrentUser abstraction for dependency injection.
    Application services receive this instead of raw JWT details.
    """

    user_id: str
    username: str
    email: str
    role: UserRole
    is_active: bool
    full_name: str | None = None
    sid: str | None = None  # Track session ID

    @classmethod
    def from_user(cls, user: User, sid: str | None = None) -> "CurrentUser":
        return cls(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            full_name=user.full_name,
            sid=sid,
        )

    def to_user(self) -> User:
        """Convert back to domain User model for service logic."""
        return User(
            user_id=self.user_id,
            username=self.username,
            email=self.email,
            hashed_password="",  # Sensitive data not kept in CurrentUser
            role=self.role,
            is_active=self.is_active,
            full_name=self.full_name,
        )

    def has_role(self, role: UserRole) -> bool:
        return self.role == role

    def has_any_role(self, roles: List[UserRole]) -> bool:
        return self.role in roles


async def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    user_repository: UserRepository = Depends(get_user_repository),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    auth_service: AuthService = Depends(get_auth_service),
) -> CurrentUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        logger.warning("Authentication failed: No token provided")
        raise credentials_exception

    # Combined check for JTI and SID revocation
    if auth_service.is_token_revoked(token):
        logger.warning("Authentication failed: Token or Session has been revoked")
        raise credentials_exception

    payload = jwt_manager.decode_access_token(token)
    if payload is None:
        logger.warning("Authentication failed: Invalid token")
        raise credentials_exception

    user_id: str = payload.get("sub")
    sid: str = payload.get("sid")
    if user_id is None:
        logger.warning("Authentication failed: Token missing subject")
        raise credentials_exception

    # Set user_id in context for observability and persistence
    set_user_id(user_id)

    user = user_repository.get_by_id(user_id)
    if user is None:
        logger.warning(f"Authentication failed: User {user_id} not found")
        raise credentials_exception

    if not user.is_active:
        logger.warning(f"Authentication failed: User {user_id} is inactive")
        raise HTTPException(status_code=400, detail="Inactive user")

    return CurrentUser.from_user(user, sid=sid)


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def rate_limit(
    request: Request,
    limiter: RateLimiterService = Depends(get_rate_limiter_service),
    current_user: CurrentUser | None = Depends(get_current_user),
):
    """
    Tiered rate limiting dependency.
    """
    user_id = current_user.user_id if current_user else None
    # For now tenant_id is None as we don't have multi-tenancy models yet
    tenant_id = None

    if not await limiter.check_all(
        ip_address=request.client.host,
        user_id=user_id,
        tenant_id=tenant_id,
        path=request.url.path,
        method=request.method,
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )
    return True


async def check_payload_size(
    request: Request,
    settings=Depends(get_settings_provider),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Strictly enforce Content-Length for protection against DoS.
    """
    content_length = request.headers.get("Content-Length")
    if content_length:
        size = int(content_length)
        if size > settings.max_payload_size_bytes:
            audit_service.log(
                event_type=AuditEventType.PAYLOAD_TOO_LARGE,
                action="payload_check",
                status="failure",
                details={
                    "payload_size": size,
                    "max_size": settings.max_payload_size_bytes,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request payload exceeds maximum allowed size",
            )
    return True


class PermissionChecker:
    """
    Dependency for checking granular permissions.
    """

    def __init__(self, permission: Permission):
        self.permission = permission

    def __call__(
        self,
        current_user: CurrentUser = Depends(get_current_user),
        authz_service: AuthorizationService = Depends(get_authorization_service),
    ) -> CurrentUser:
        if not authz_service.has_permission(current_user.to_user(), self.permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {self.permission}",
            )
        return current_user


class RoleChecker:
    """
    Dependency for checking user roles (Legacy/Coarse-grained).
    """

    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(
        self, current_user: CurrentUser = Depends(get_current_user)
    ) -> CurrentUser:
        if current_user.role not in self.allowed_roles:
            logger.warning(
                f"Authorization failed: User {current_user.username} with role "
                f"{current_user.role} attempted to access resource requiring "
                f"roles {[r.value for r in self.allowed_roles]}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user


# Shorthand dependency factories
def require_permission(permission: Permission):
    return PermissionChecker(permission)


def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
