import time
from datetime import timedelta, timezone
from typing import Optional, Tuple, Dict, Any
from app.domain.models.user import User
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.revocation_repository import RevocationRepository
from app.core.security.password import PasswordHasher
from app.core.security.jwt import JWTManager, TokenType
from app.core.observability.logger import get_logger

logger = get_logger(__name__)

class AuthService:
    """
    Coordinates authentication operations.
    Supports access tokens, refresh tokens, and token revocation.
    """
    def __init__(
        self,
        user_repository: UserRepository,
        jwt_manager: JWTManager,
        revocation_repository: RevocationRepository
    ):
        self.user_repository = user_repository
        self.jwt_manager = jwt_manager
        self.revocation_repository = revocation_repository

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.user_repository.get_by_username(username)
        if not user:
            logger.warning(f"Authentication failed: User {username} not found")
            return None

        if not PasswordHasher.verify(password, user.hashed_password):
            logger.warning(f"Authentication failed: Incorrect password for user {username}")
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: User {username} is inactive")
            return None

        return user

    def create_tokens(self, user: User) -> Dict[str, Any]:
        access_token, refresh_token = self.jwt_manager.create_token_pair(
            data={"sub": user.user_id, "role": user.role.value, "username": user.username}
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.jwt_manager.access_token_expire_minutes * 60,
        }

    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        payload = self.jwt_manager.decode_refresh_token(refresh_token)
        if not payload:
            logger.warning("Token refresh failed: Invalid refresh token")
            return None

        if self.is_token_revoked(refresh_token):
            logger.warning("Token refresh failed: Token has been revoked")
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        user = self.user_repository.get_by_id(user_id)
        if not user or not user.is_active:
            logger.warning(f"Token refresh failed: User {user_id} not found or inactive")
            return None

        new_access_token = self.jwt_manager.create_access_token(
            data={"sub": user.user_id, "role": user.role.value, "username": user.username}
        )
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": self.jwt_manager.access_token_expire_minutes * 60,
        }

    def revoke_token(self, token: str) -> bool:
        expiry = self.jwt_manager.get_token_expiry(token)
        if not expiry:
            return False

        now = time.time()
        ttl = int(expiry.timestamp() - now)

        if ttl > 0:
            self.revocation_repository.revoke(token, ttl)
            return True
        return False

    def is_token_revoked(self, token: str) -> bool:
        return self.revocation_repository.is_revoked(token)

    def get_user_from_token(self, token: str) -> Optional[User]:
        payload = self.jwt_manager.decode_access_token(token)
        if not payload:
            return None

        if self.is_token_revoked(token):
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        return self.user_repository.get_by_id(user_id)
