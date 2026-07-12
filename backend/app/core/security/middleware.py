from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config.base import Settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers to all responses.
    Implements OWASP Secure Headers recommendations for APIs.
    """

    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Content Security Policy - restrictive for API
        if self.settings.environment == "production":
            response.headers["Content-Security-Policy"] = (
                "default-src 'none'; "
                "frame-ancestors 'none'; "
                "form-action 'none'; "
                "base-uri 'none'"
            )
        else:
            # Allow swagger UI in development
            response.headers["Content-Security-Policy"] = (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval' data:; "
                "frame-ancestors 'none'; "
                "form-action 'self'"
            )

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (Feature Policy)
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=(), "
            "display-capture=(), document-domain=(), encrypted-media=(), "
            "fullscreen=(), gamepad=(), midi=(), picture-in-picture=()"
        )

        # XSS Protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Remove server-identifying headers
        if "Server" in response.headers:
            del response.headers["Server"]

        # HSTS in production (only if behind HTTPS)
        if self.settings.environment == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response


class CORSMiddlewareConfig:
    """
    Configuration builder for CORS middleware.
    Supports environment-specific settings.
    """

    @staticmethod
    def get_cors_config(settings: Settings) -> dict:
        if settings.environment == "production":
            # Production: Strict CORS - specific origins only
            return {
                "allow_origins": settings.cors_allowed_origins,
                "allow_credentials": True,
                "allow_methods": settings.cors_allowed_methods,
                "allow_headers": settings.cors_allowed_headers,
                "expose_headers": [
                    "X-Request-ID",
                    "X-Correlation-ID",
                    "X-Process-Time",
                ],
                "max_age": 600,
            }
        elif settings.environment == "testing":
            # Testing: Allow localhost and test origins
            return {
                "allow_origins": [
                    "http://localhost",
                    "http://localhost:3000",
                    "http://testserver",
                ],
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"],
                "expose_headers": [
                    "X-Request-ID",
                    "X-Correlation-ID",
                    "X-Process-Time",
                ],
            }
        else:
            # Development: More permissive but still controlled
            return {
                "allow_origins": (
                    settings.cors_allowed_origins
                    if settings.cors_allowed_origins != ["*"]
                    else [
                        "http://localhost:3000",
                        "http://localhost:8000",
                        "http://127.0.0.1:3000",
                        "http://127.0.0.1:8000",
                    ]
                ),
                "allow_credentials": True,
                "allow_methods": settings.cors_allowed_methods,
                "allow_headers": settings.cors_allowed_headers,
                "expose_headers": [
                    "X-Request-ID",
                    "X-Correlation-ID",
                    "X-Process-Time",
                ],
            }


def setup_security(app: FastAPI, settings: Settings):
    """
    Configure CORS, Security Headers, and other security middlewares.
    """
    # CORS - Environment-specific configuration
    cors_config = CORSMiddlewareConfig.get_cors_config(settings)
    app.add_middleware(CORSMiddleware, **cors_config)

    # Security Headers
    app.add_middleware(SecurityHeadersMiddleware, settings=settings)
