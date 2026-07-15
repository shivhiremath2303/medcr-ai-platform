import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, Optional, Tuple

import jwt
from pydantic import SecretStr

from app.core.config.base import Settings


class TokenType(str):
    ACCESS = "access"
    REFRESH = "refresh"


class JWTManager:
    """
    Utility for creating and validating JSON Web Tokens.
    Supports access tokens and refresh tokens with configurable expiration,
    JTI (JWT ID) tracking, and SID (Session ID) support.
    Handles SecretStr for secure key management.
    """

    def __init__(self, settings: Settings):
        self.secret_key = settings.jwt_secret_key.get_secret_value()
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.jwt_access_token_minutes
        self.refresh_token_expire_days = settings.jwt_refresh_token_days

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: timedelta | None = None,
        sid: str | None = None,
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update(
            {
                "exp": expire,
                "type": TokenType.ACCESS,
                "jti": str(uuid.uuid4()),
                "iat": datetime.now(UTC),
            }
        )
        if sid:
            to_encode["sid"] = sid

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(
        self,
        data: Dict[str, Any],
        expires_delta: timedelta | None = None,
        sid: str | None = None,
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(days=self.refresh_token_expire_days)

        to_encode.update(
            {
                "exp": expire,
                "type": TokenType.REFRESH,
                "jti": str(uuid.uuid4()),
                "iat": datetime.now(UTC),
            }
        )
        if sid:
            to_encode["sid"] = sid

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_token_pair(
        self,
        data: Dict[str, Any],
        access_expires: timedelta | None = None,
        refresh_expires: timedelta | None = None,
        sid: str | None = None,
    ) -> Tuple[str, str]:
        # Generate a session ID if not provided
        session_id = sid or str(uuid.uuid4())
        access_token = self.create_access_token(data, access_expires, sid=session_id)
        refresh_token = self.create_refresh_token(data, refresh_expires, sid=session_id)
        return access_token, refresh_token

    def decode_token(self, token: str) -> Dict[str, Any] | None:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None

    def decode_access_token(self, token: str) -> Dict[str, Any] | None:
        payload = self.decode_token(token)
        if payload and payload.get("type") == TokenType.ACCESS:
            return payload
        return None

    def decode_refresh_token(self, token: str) -> Dict[str, Any] | None:
        payload = self.decode_token(token)
        if payload and payload.get("type") == TokenType.REFRESH:
            return payload
        return None

    def get_token_expiry(self, token: str) -> datetime | None:
        payload = self.decode_token(token)
        if payload and "exp" in payload:
            return datetime.fromtimestamp(payload["exp"], tz=UTC)
        return None

    def is_token_expired(self, token: str) -> bool:
        expiry = self.get_token_expiry(token)
        if expiry:
            return datetime.now(UTC) >= expiry
        return True
