import contextvars
from typing import Optional

# Context variables for observability and persistence
request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)
correlation_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "correlation_id", default=None
)
user_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "user_id", default=None
)
tenant_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "tenant_id", default=None
)


def get_request_id() -> str | None:
    return request_id_var.get()


def set_request_id(request_id: str) -> None:
    request_id_var.set(request_id)


def get_correlation_id() -> str | None:
    return correlation_id_var.get()


def set_correlation_id(correlation_id: str) -> None:
    correlation_id_var.set(correlation_id)


def get_user_id() -> str | None:
    return user_id_var.get()


def set_user_id(user_id: str) -> None:
    user_id_var.set(user_id)


def get_tenant_id() -> str | None:
    return tenant_id_var.get()


def set_tenant_id(tenant_id: str | None) -> None:
    tenant_id_var.set(tenant_id)
