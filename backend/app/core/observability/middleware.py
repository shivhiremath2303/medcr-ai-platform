import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.observability.context import set_correlation_id, set_request_id
from app.core.observability.logger import get_logger

logger = get_logger(__name__)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling Request ID, Correlation ID, and logging requests.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()

        # Extract or generate Correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        set_correlation_id(correlation_id)

        # Generate Request ID
        request_id = str(uuid.uuid4())
        set_request_id(request_id)

        # Process the request
        try:
            response = await call_next(request)

            process_time = time.perf_counter() - start_time
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Process-Time"] = str(process_time)

            logger.info(
                f"Request finished: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - Duration: {process_time:.4f}s"
            )

            return response

        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} - "
                f"Error: {str(e)} - Duration: {process_time:.4f}s",
                exc_info=True,
            )
            raise
