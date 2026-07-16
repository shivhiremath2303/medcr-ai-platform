from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.observability.logger import get_logger
from app.core.security.auth_service import AuthService
from app.core.security.dependencies import (
    CurrentUser,
    get_current_active_user,
    get_current_user,
    rate_limit,
)
from app.di import get_audit_service, get_auth_service, get_membership_repository
from app.domain.models.audit import AuditEventType
from app.domain.repositories.tenant_repository import MembershipRepository
from app.services.audit.audit_service import AuditService

router = APIRouter(
    prefix="/auth",
    tags=["Security"],
    dependencies=[Depends(rate_limit)],
)

logger = get_logger(__name__)


@router.post("/login", summary="Create access token")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    audit_service: AuditService = Depends(get_audit_service),
):
    # Tiered rate limiting is handled by router-level dependency

    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        # AuthService already logs failure
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = await auth_service.create_tokens(user)
    return tokens


@router.post("/refresh", summary="Refresh access token with rotation")
async def refresh_token(
    request: Request,
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service),
):
    # Tiered rate limiting is handled by router-level dependency

    refreshed = await auth_service.refresh_access_token(refresh_token)
    if not refreshed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or reused refresh token. Session terminated.",
        )
    return refreshed


@router.post("/revoke", summary="Revoke current token")
async def revoke_token(
    token: str,
    current_user: CurrentUser = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    audit_service: AuditService = Depends(get_audit_service),
):
    success = auth_service.revoke_token(token)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to revoke token")
    return {"detail": "Token revoked"}


@router.post("/logout", summary="Logout (Revoke entire session)")
async def logout(
    current_user: CurrentUser = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    audit_service: AuditService = Depends(get_audit_service),
):
    if not current_user.sid:
        raise HTTPException(status_code=400, detail="No session found")

    auth_service.revoke_session(current_user.sid)
    audit_service.log(
        AuditEventType.LOGOUT,
        action="user_logout",
        user_id=current_user.user_id,
        username=current_user.username,
        details={"sid": current_user.sid},
    )
    return {"detail": "Successfully logged out"}


@router.post("/switch-tenant", summary="Switch active tenant context")
async def switch_tenant(
    tenant_id: str,
    current_user: CurrentUser = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
    membership_repo: MembershipRepository = Depends(get_membership_repository),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Switch the active tenant context for the current session.
    Verifies membership and re-issues tokens with the new tenant claim.
    """
    # 1. Verify user belongs to the target tenant
    membership = await membership_repo.get(current_user.user_id, tenant_id)
    if not membership or not membership.is_active:
        audit_service.log(
            AuditEventType.ACCESS_DENIED,
            action="switch_tenant",
            status="failure",
            user_id=current_user.user_id,
            details={"target_tenant_id": tenant_id, "reason": "no_membership"},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this tenant",
        )

    # 2. Re-issue tokens with the new tenant_id claim
    # Note: to_user() returns a domain model without sensitive password data
    tokens = await auth_service.create_tokens(
        current_user.to_user(), tenant_id=tenant_id
    )

    audit_service.log(
        AuditEventType.TOKEN_REFRESH,
        action="switch_tenant",
        status="success",
        user_id=current_user.user_id,
        details={"new_tenant_id": tenant_id},
    )

    return tokens
