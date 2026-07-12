from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.observability.logger import get_logger
from app.core.security.auth_service import AuthService
from app.core.security.dependencies import CurrentUser, get_current_user
from app.core.security.rate_limiter import RateLimiterService
from app.di import get_auth_service, get_rate_limiter_service

router = APIRouter(
    prefix="/auth",
    tags=["Security"],
)

logger = get_logger(__name__)


@router.post("/login", summary="Create access token")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    limiter: RateLimiterService = Depends(get_rate_limiter_service),
):
    # Rate limit login attempts by identifier (username or IP)
    identifier = form_data.username or request.client.host
    if not await limiter.check(identifier, request.url.path, request.method):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )

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
    limiter: RateLimiterService = Depends(get_rate_limiter_service),
):
    # Rate limit by IP for refresh
    client_host = request.client.host if request.client else "unknown"
    if not await limiter.check(client_host, request.url.path, request.method):
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
    success = auth_service.revoke_token(token)
    if not success:
        raise HTTPException(status_code=400, detail="Unable to revoke token")
    logger.info("Token revoked", extra_data={"user_id": current_user.user_id})
    return {"detail": "Token revoked"}
