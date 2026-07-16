from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models.tenant import Membership, Organization, Tenant, Workspace


class OrganizationRepository(ABC):
    @abstractmethod
    async def get_by_id(self, organization_id: str) -> Optional[Organization]:
        """Retrieve an organization by ID."""

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        """Retrieve an organization by slug."""

    @abstractmethod
    async def save(self, organization: Organization) -> Organization:
        """Save an organization."""

    @abstractmethod
    async def list_all(self) -> List[Organization]:
        """List all organizations."""


class TenantRepository(ABC):
    @abstractmethod
    async def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        """Retrieve a tenant by ID."""

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        """Retrieve a tenant by slug."""

    @abstractmethod
    async def list_by_organization(self, organization_id: str) -> List[Tenant]:
        """List all tenants belonging to an organization."""

    @abstractmethod
    async def save(self, tenant: Tenant) -> Tenant:
        """Save a tenant."""


class WorkspaceRepository(ABC):
    @abstractmethod
    async def get_by_id(self, workspace_id: str) -> Optional[Workspace]:
        """Retrieve a workspace by ID."""

    @abstractmethod
    async def list_by_tenant(self, tenant_id: str) -> List[Workspace]:
        """List all workspaces belonging to a tenant."""

    @abstractmethod
    async def save(self, workspace: Workspace) -> Workspace:
        """Save a workspace."""

    @abstractmethod
    async def delete(self, workspace_id: str) -> bool:
        """Delete a workspace."""


class MembershipRepository(ABC):
    @abstractmethod
    async def get(self, user_id: str, tenant_id: str) -> Optional[Membership]:
        """Get a specific membership."""

    @abstractmethod
    async def list_by_user(self, user_id: str) -> List[Membership]:
        """List all memberships for a user."""

    @abstractmethod
    async def list_by_tenant(self, tenant_id: str) -> List[Membership]:
        """List all memberships for a tenant."""

    @abstractmethod
    async def save(self, membership: Membership) -> Membership:
        """Save a membership."""

    @abstractmethod
    async def delete(self, user_id: str, tenant_id: str) -> bool:
        """Remove a user from a tenant."""
