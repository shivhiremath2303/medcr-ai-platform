from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security.auth_service import AuthService
from app.di import get_auth_service
from app.core.security.dependencies import get_current_user, CurrentUser
from app.core.security.rate_limiter import get_rate_limiter_service
from app.core.observability.logger import get_logger

router = APIRouter(
    prefix="/auth",
    tags=["Security"],
)

logger = get_logger(__name__)


@router.post("/login", summary="Create access token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = auth_service.create_tokens(user)
    logger.info(
        "Authentication success",
        extra_data={"username": user.username, "user_id": user.user_id},
    )
    return tokens


@router.post("/refresh", summary="Refresh access token")
async def refresh_token(
    request: Request,
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service),
    limiter=Depends(get_rate_limiter_service),
):
    # Rate limit by IP for refresh
    client_host = request.client.host if request.client else "unknown"
    rl = limiter.check_rate_limit(client_host, request.url.path, request.method)
    if not rl.allowed:
        raise HTTPException(status_code=429, detail="Too Many Requests")

    refreshed = auth_service.refresh_access_token(refresh_token)
    if not refreshed:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    logger.info("Token refreshed", extra_data={"client": client_host})
    return refreshed


@router.post("/revoke", summary="Revoke token")
async def revoke_token(
    token: str,
    current_user: CurrentUser = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    # Only allow users to revoke their own tokens (future: admin revoke)
    success = auth_service.revoke_token(token)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to revoke token")
    logger.info("Token revoked", extra_data={"user_id": current_user.user_id})
    return {"detail": "Token revoked"}
