import pytest

from app.core.security.authorization import AuthorizationService
from app.domain.models.user import User, UserRole
from app.services.audit.audit_service import AuditService


@pytest.fixture
def authz_service():
    return AuthorizationService(audit_service=AuditService())


@pytest.fixture
def user_a():
    return User(
        user_id="user-a",
        username="user_a",
        email="a@tenant.com",
        hashed_password="",
        role=UserRole.LAWYER,
    )


@pytest.fixture
def user_b():
    return User(
        user_id="user-b",
        username="user_b",
        email="b@tenant.com",
        hashed_password="",
        role=UserRole.LAWYER,
    )


def test_tenant_isolation_logic(authz_service, user_a, user_b):
    """
    Verify that AuthorizationService correctly enforces tenant isolation.
    """
    tenant_a = "tenant-a"
    tenant_b = "tenant-b"

    # Document metadata for a resource in Tenant A
    doc_metadata_a = {"tenant_id": tenant_a, "owner_id": "user-a"}

    # 1. User A should access their own tenant's document
    assert (
        authz_service.can_access_document(
            user=user_a, document_metadata=doc_metadata_a, user_tenant_id=tenant_a
        )
        is True
    )

    # 2. User B (Tenant B) should NOT access Tenant A's document
    assert (
        authz_service.can_access_document(
            user=user_b, document_metadata=doc_metadata_a, user_tenant_id=tenant_b
        )
        is False
    )

    # 3. Global resource (no tenant_id) should be accessible (fallback)
    global_doc_metadata = {"tenant_id": None}
    assert (
        authz_service.can_access_document(
            user=user_b, document_metadata=global_doc_metadata, user_tenant_id=tenant_b
        )
        is True
    )


def test_tenant_switching_context(authz_service, user_a):
    """
    Verify that changing the active tenant context changes access results.
    """
    tenant_a = "tenant-a"
    tenant_b = "tenant-b"

    doc_metadata_b = {"tenant_id": tenant_b}

    # User A currently in Tenant A
    assert (
        authz_service.can_access_document(
            user=user_a, document_metadata=doc_metadata_b, user_tenant_id=tenant_a
        )
        is False
    )

    # User A switches to Tenant B (e.g., via membership)
    assert (
        authz_service.can_access_document(
            user=user_a, document_metadata=doc_metadata_b, user_tenant_id=tenant_b
        )
        is True
    )
