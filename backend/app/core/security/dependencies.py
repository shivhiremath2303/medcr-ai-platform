from dataclasses import dataclass
from typing import Optional, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from app.domain.models.user import User, UserRole
from app.domain.repositories.user_repository import UserRepository
from app.core.security.jwt import JWTManager
from app.core.security.auth_service import AuthService
from app.di import get_user_repository, get_jwt_manager, get_auth_service
from app.core.observability.logger import get_logger
from app.core.observability.context import set_user_id

logger = get_logger(__name__)

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
    full_name: Optional[str] = None

    @classmethod
    def from_user(cls, user: User) -> "CurrentUser":
        return cls(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            full_name=user.full_name,
        )

    def has_role(self, role: UserRole) -> bool:
        return self.role == role

    def has_any_role(self, roles: List[UserRole]) -> bool:
        return self.role in roles

async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
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

    if auth_service.is_token_revoked(token):
        logger.warning("Authentication failed: Token has been revoked")
        raise credentials_exception

    payload = jwt_manager.decode_access_token(token)
    if payload is None:
        logger.warning("Authentication failed: Invalid token")
        raise credentials_exception

    user_id: str = payload.get("sub")
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

    return CurrentUser.from_user(user)

async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

class RoleChecker:
    """
    Dependency for checking user roles.
    """
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
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

def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def require_lawyer_or_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.role not in [UserRole.ADMIN, UserRole.LAWYER]:
        raise HTTPException(status_code=403, detail="Lawyer or admin access required")
    return current_user
