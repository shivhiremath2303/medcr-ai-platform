import time
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import get_settings
from app.core.observability.logger import get_logger
from app.core.observability.metrics import MetricsRegistry
from app.core.security.jwt import JWTManager, TokenType
from app.core.security.password import PasswordHasher
from app.domain.models.audit import AuditEventType
from app.domain.models.user import User
from app.domain.repositories.revocation_repository import RevocationRepository
from app.domain.repositories.tenant_repository import MembershipRepository
from app.domain.repositories.user_repository import UserRepository
from app.services.audit.audit_service import AuditService

logger = get_logger(__name__)
settings = get_settings()


class AuthService:
    """
    Coordinates authentication operations with enterprise hardening, auditing, and analytics.
    Supports token rotation, session management, and account lockout.
    Now enhanced with Multi-Tenant awareness (10.4.3).
    """

    def __init__(
        self,
        user_repository: UserRepository,
        jwt_manager: JWTManager,
        revocation_repository: RevocationRepository,
        audit_service: AuditService,
        metrics: MetricsRegistry,
        membership_repository: MembershipRepository,
    ):
        self.user_repository = user_repository
        self.jwt_manager = jwt_manager
        self.revocation_repository = revocation_repository
        self.audit_service = audit_service
        self.metrics = metrics
        self.membership_repository = membership_repository

    async def authenticate_user(self, username: str, password: str) -> User | None:
        """
        Authenticate a user by username and password.
        Supports account lockout and auditing.
        """
        # Check if account/username is locked out
        if self.revocation_repository.is_locked_out(username):
            self.audit_service.log(
                AuditEventType.LOGIN_FAILURE,
                action="user_login",
                status="failure",
                username=username,
                details={"reason": "account_locked"},
            )
            return None

        # UserRepo is currently sync (Redis/Memory)
        user = self.user_repository.get_by_username(username)
        if not user:
            self._handle_failed_login(username, reason="user_not_found")
            return None

        if not PasswordHasher.verify(password, user.hashed_password):
            self._handle_failed_login(
                username, reason="invalid_password", user_id=user.user_id
            )
            return None

        if not user.is_active:
            self.audit_service.log(
                AuditEventType.LOGIN_FAILURE,
                action="user_login",
                status="failure",
                user_id=user.user_id,
                username=username,
                details={"reason": "user_inactive"},
            )
            return None

        # Reset failures on successful login
        self.revocation_repository.reset_failed_login(username)

        # Operational Analytics (10.2.9)
        self.metrics.track_user_activity(action="user_login", role=user.role.value)

        self.audit_service.log(
            AuditEventType.LOGIN_SUCCESS,
            action="user_login",
            user_id=user.user_id,
            username=username,
        )
        return user

    async def create_tokens(self, user: User, tenant_id: str | None = None) -> Dict[str, Any]:
        """
        Creates a token pair. If tenant_id is provided, it's included in the claims.
        If not provided, the user's primary tenant (if any) is used.
        """
        # Multi-Tenant: Resolve tenant context (Async SQL check)
        target_tenant_id = tenant_id
        if not target_tenant_id:
            memberships = await self.membership_repository.list_by_user(user.user_id)
            if memberships:
                # Default to the first membership found for now
                target_tenant_id = memberships[0].tenant_id

        # Check concurrent session limit
        active_sessions = self.revocation_repository.get_user_sessions(user.user_id)
        if len(active_sessions) >= settings.auth_max_sessions:
            logger.warning(f"Session limit reached for user {user.user_id}.")

        token_data = {
            "sub": user.user_id,
            "role": user.role.value,
            "username": user.username,
        }
        if target_tenant_id:
            token_data["tenant_id"] = target_tenant_id

        access_token, refresh_token = self.jwt_manager.create_token_pair(data=token_data)

        payload = self.jwt_manager.decode_token(access_token)
        sid = payload.get("sid") if payload else None
        if not isinstance(sid, str):
            raise RuntimeError("Newly issued access token is missing a session ID")

        ttl_seconds = settings.jwt_refresh_token_days * 24 * 3600
        self.revocation_repository.add_session(user.user_id, sid, ttl_seconds)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.jwt_manager.access_token_expire_minutes * 60,
            "tenant_id": target_tenant_id,
        }

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any] | None:
        """
        Rotates a refresh token and issues a new access/refresh pair.
        Supports token reuse detection.
        """
        payload = self.jwt_manager.decode_refresh_token(refresh_token)
        if not payload:
            return None

        jti = payload.get("jti")
        sid = payload.get("sid")
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        if not isinstance(jti, str) or not isinstance(sid, str) or not isinstance(user_id, str):
            return None

        if self.revocation_repository.is_revoked(jti):
            self.audit_service.log(
                AuditEventType.TOKEN_REFRESH,
                action="token_rotation",
                status="failure",
                user_id=user_id,
                details={"reason": "token_reuse_detected", "jti": jti},
            )
            self.revoke_session(sid)
            return None

        if self.revocation_repository.is_revoked(sid):
            return None

        user = self.user_repository.get_by_id(user_id)
        if not user or not user.is_active:
            return None

        expiry = self.jwt_manager.get_token_expiry(refresh_token)
        if expiry:
            ttl = int((expiry - datetime.now(UTC)).total_seconds())
            if ttl > 0:
                self.revocation_repository.revoke(jti, ttl)

        token_data = {
            "sub": user.user_id,
            "role": user.role.value,
            "username": user.username,
        }
        if tenant_id:
            token_data["tenant_id"] = tenant_id

        new_access_token, new_refresh_token = self.jwt_manager.create_token_pair(
            data=token_data,
            sid=sid,
        )

        self.audit_service.log(
            AuditEventType.TOKEN_REFRESH,
            action="token_rotation",
            user_id=user.user_id,
            details={"sid": sid, "tenant_id": tenant_id},
        )

        # Operational Analytics (10.2.9)
        self.metrics.track_user_activity(action="token_refresh", role=user.role.value)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": self.jwt_manager.access_token_expire_minutes * 60,
            "tenant_id": tenant_id,
        }

    def revoke_token(self, token: str) -> bool:
        payload = self.jwt_manager.decode_token(token)
        if not payload:
            return False

        jti = payload.get("jti")
        user_id = payload.get("sub")
        expiry = self.jwt_manager.get_token_expiry(token)
        if not isinstance(jti, str) or not isinstance(user_id, str) or not expiry:
            return False

        ttl = int((expiry - datetime.now(UTC)).total_seconds())
        if ttl > 0:
            self.revocation_repository.revoke(jti, ttl)
            self.audit_service.log(
                AuditEventType.TOKEN_REVOKE,
                action="revoke_token",
                user_id=user_id,
                details={"jti": jti},
            )
            return True
        return False

    def revoke_session(self, sid: str) -> bool:
        ttl = settings.jwt_refresh_token_days * 24 * 3600
        self.revocation_repository.revoke(sid, ttl)
        self.audit_service.log(
            AuditEventType.LOGOUT,
            action="revoke_session",
            details={"sid": sid},
        )
        return True

    def is_token_revoked(self, token: str) -> bool:
        payload = self.jwt_manager.decode_token(token)
        if not payload:
            return True

        jti = payload.get("jti")
        sid = payload.get("sid")

        if jti and self.revocation_repository.is_revoked(jti):
            return True
        if sid and self.revocation_repository.is_revoked(sid):
            return True

        return False

    def get_user_from_token(self, token: str) -> User | None:
        payload = self.jwt_manager.decode_access_token(token)
        if not payload or self.is_token_revoked(token):
            return None

        user_id = payload.get("sub")
        return (
            self.user_repository.get_by_id(user_id)
            if isinstance(user_id, str)
            else None
        )

    def _handle_failed_login(
        self, username: str, reason: str, user_id: str | None = None
    ):
        """Track failures and enforce lockout."""
        count = self.revocation_repository.increment_failed_login(
            username, settings.rate_limit_window_seconds
        )

        self.audit_service.log(
            AuditEventType.LOGIN_FAILURE,
            action="user_login",
            status="failure",
            user_id=user_id,
            username=username,
            details={"reason": reason, "failure_count": count},
        )

        # Operational Analytics (10.2.9)
        self.metrics.track_user_activity(action="login_failure", role="unknown")

        if count >= settings.auth_lockout_threshold:
            # Operational Analytics (10.2.9)
            self.metrics.track_user_activity(action="account_lockout", role="unknown")

            self.audit_service.log(
                AuditEventType.ACCOUNT_LOCKOUT,
                action="account_lockout",
                status="failure",
                username=username,
                details={"threshold": settings.auth_lockout_threshold},
            )
            self.revocation_repository.set_lockout(
                username, settings.auth_lockout_minutes * 60
            )
