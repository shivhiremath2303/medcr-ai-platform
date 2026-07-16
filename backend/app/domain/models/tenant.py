from datetime import UTC, datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field


class TenantStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"
    PENDING = "pending"


class TenantRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"


class Organization(BaseModel):
    """
    Top-level legal entity for billing and account management.
    An Organization can own multiple Tenants.
    """

    organization_id: str
    name: str
    slug: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict = Field(default_factory=dict)


class Tenant(BaseModel):
    """
    Primary unit of data isolation.
    All resources (documents, vectors, cache) are siloed by tenant_id.
    """

    tenant_id: str
    organization_id: str
    name: str
    slug: str
    status: TenantStatus = TenantStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Isolation Configuration
    dedicated_db: bool = False
    dedicated_vector_index: bool = False

    settings: dict = Field(default_factory=dict)


class Workspace(BaseModel):
    """
    Logical grouping within a Tenant (e.g., a specific case or department).
    Provides a second layer of organization within the tenant.
    """

    workspace_id: str
    tenant_id: str
    name: str
    description: Optional[str] = None
    is_default: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict = Field(default_factory=dict)


class Membership(BaseModel):
    """
    Relationship between a User and a Tenant.
    Users can belong to multiple tenants with different roles.
    """

    user_id: str
    tenant_id: str
    role: TenantRole
    joined_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
