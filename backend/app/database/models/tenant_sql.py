from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from app.domain.models.tenant import TenantRole, TenantStatus
from app.infrastructure.storage.database_foundation import Base


class SQLOrganization(Base):
    __tablename__ = "organizations"

    organization_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
    metadata_json = Column(JSON, default=dict)

    tenants = relationship(
        "SQLTenant", back_populates="organization", cascade="all, delete-orphan"
    )


class SQLTenant(Base):
    __tablename__ = "tenants"

    tenant_id = Column(String, primary_key=True, index=True)
    organization_id = Column(
        String, ForeignKey("organizations.organization_id"), nullable=False
    )
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    status = Column(Enum(TenantStatus), default=TenantStatus.ACTIVE)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    dedicated_db = Column(Boolean, default=False)
    dedicated_vector_index = Column(Boolean, default=False)
    settings = Column(JSON, default=dict)

    organization = relationship("SQLOrganization", back_populates="tenants")
    workspaces = relationship(
        "SQLWorkspace", back_populates="tenant", cascade="all, delete-orphan"
    )
    memberships = relationship(
        "SQLMembership", back_populates="tenant", cascade="all, delete-orphan"
    )


class SQLWorkspace(Base):
    __tablename__ = "workspaces"

    workspace_id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
    metadata_json = Column(JSON, default=dict)

    tenant = relationship("SQLTenant", back_populates="workspaces")


class SQLMembership(Base):
    __tablename__ = "memberships"

    user_id = Column(String, primary_key=True, index=True)
    tenant_id = Column(
        String, ForeignKey("tenants.tenant_id"), primary_key=True, index=True
    )
    role = Column(Enum(TenantRole), default=TenantRole.MEMBER)
    joined_at = Column(DateTime, default=lambda: datetime.now(UTC))
    is_active = Column(Boolean, default=True)

    tenant = relationship("SQLTenant", back_populates="memberships")
