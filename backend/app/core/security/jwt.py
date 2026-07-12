from datetime import UTC, datetime, timedelta
from typing import Any, Dict, Optional, Tuple

import jwt
from app.core.config.base import Settings


class TokenType(str):
    ACCESS = "access"
    REFRESH = "refresh"


class JWTManager:
    """
    Utility for creating and validating JSON Web Tokens.
    Supports access tokens and refresh tokens with configurable expiration.
    """

    def __init__(self, settings: Settings):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.jwt_access_token_minutes
        self.refresh_token_expire_days = settings.jwt_refresh_token_days

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update({"exp": expire, "type": TokenType.ACCESS})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(days=self.refresh_token_expire_days)

        to_encode.update({"exp": expire, "type": TokenType.REFRESH})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_token_pair(
        self,
        data: Dict[str, Any],
        access_expires: Optional[timedelta] = None,
        refresh_expires: Optional[timedelta] = None,
    ) -> Tuple[str, str]:
        access_token = self.create_access_token(data, access_expires)
        refresh_token = self.create_refresh_token(data, refresh_expires)
        return access_token, refresh_token

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None

    def decode_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        payload = self.decode_token(token)
        if payload and payload.get("type") == TokenType.ACCESS:
            return payload
        return None

    def decode_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        payload = self.decode_token(token)
        if payload and payload.get("type") == TokenType.REFRESH:
            return payload
        return None

    def get_token_expiry(self, token: str) -> Optional[Dict[str, Any]]:
        payload = self.decode_token(token)
        if payload and "exp" in payload:
            return datetime.fromtimestamp(payload["exp"], tz=UTC)
        return None

    def is_token_expired(self, token: str) -> bool:
        expiry = self.get_token_expiry(token)
        if expiry:
            return datetime.now(UTC) >= expiry
        return True
