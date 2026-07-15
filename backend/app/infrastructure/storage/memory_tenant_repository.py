from typing import Dict, List, Optional

from app.domain.models.tenant import Membership, Organization, Tenant, Workspace
from app.domain.repositories.tenant_repository import (
    MembershipRepository,
    OrganizationRepository,
    TenantRepository,
    WorkspaceRepository,
)


class MemoryOrganizationRepository(OrganizationRepository):
    def __init__(self):
        self._organizations: Dict[str, Organization] = {}

    def get_by_id(self, organization_id: str) -> Optional[Organization]:
        return self._organizations.get(organization_id)

    def get_by_slug(self, slug: str) -> Optional[Organization]:
        return next((o for o in self._organizations.values() if o.slug == slug), None)

    def save(self, organization: Organization) -> Organization:
        self._organizations[organization.organization_id] = organization
        return organization

    def list_all(self) -> List[Organization]:
        return list(self._organizations.values())


class MemoryTenantRepository(TenantRepository):
    def __init__(self):
        self._tenants: Dict[str, Tenant] = {}

    def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        return self._tenants.get(tenant_id)

    def get_by_slug(self, slug: str) -> Optional[Tenant]:
        return next((t for t in self._tenants.values() if t.slug == slug), None)

    def list_by_organization(self, organization_id: str) -> List[Tenant]:
        return [t for t in self._tenants.values() if t.organization_id == organization_id]

    def save(self, tenant: Tenant) -> Tenant:
        self._tenants[tenant.tenant_id] = tenant
        return tenant


class MemoryWorkspaceRepository(WorkspaceRepository):
    def __init__(self):
        self._workspaces: Dict[str, Workspace] = {}

    def get_by_id(self, workspace_id: str) -> Optional[Workspace]:
        return self._workspaces.get(workspace_id)

    def list_by_tenant(self, tenant_id: str) -> List[Workspace]:
        return [w for w in self._workspaces.values() if w.tenant_id == tenant_id]

    def save(self, workspace: Workspace) -> Workspace:
        self._workspaces[workspace.workspace_id] = workspace
        return workspace

    def delete(self, workspace_id: str) -> bool:
        if workspace_id in self._workspaces:
            del self._workspaces[workspace_id]
            return True
        return False


class MemoryMembershipRepository(MembershipRepository):
    def __init__(self):
        self._memberships: List[Membership] = []

    def get(self, user_id: str, tenant_id: str) -> Optional[Membership]:
        return next(
            (m for m in self._memberships if m.user_id == user_id and m.tenant_id == tenant_id),
            None,
        )

    def list_by_user(self, user_id: str) -> List[Membership]:
        return [m for m in self._memberships if m.user_id == user_id]

    def list_by_tenant(self, tenant_id: str) -> List[Membership]:
        return [m for m in self._memberships if m.tenant_id == tenant_id]

    def save(self, membership: Membership) -> Membership:
        existing = self.get(membership.user_id, membership.tenant_id)
        if existing:
            self._memberships.remove(existing)
        self._memberships.append(membership)
        return membership

    def delete(self, user_id: str, tenant_id: str) -> bool:
        existing = self.get(user_id, tenant_id)
        if existing:
            self._memberships.remove(existing)
            return True
        return False
