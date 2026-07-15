from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.tenant_sql import (
    SQLMembership,
    SQLOrganization,
    SQLTenant,
    SQLWorkspace,
)
from app.domain.models.tenant import Membership, Organization, Tenant, Workspace
from app.domain.repositories.tenant_repository import (
    MembershipRepository,
    OrganizationRepository,
    TenantRepository,
    WorkspaceRepository,
)


class SQLOrganizationRepository(OrganizationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, organization_id: str) -> Optional[Organization]:
        result = await self.session.execute(
            select(SQLOrganization).where(SQLOrganization.organization_id == organization_id)
        )
        sql_org = result.scalar_one_or_none()
        return self._map_to_domain(sql_org) if sql_org else None

    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        result = await self.session.execute(
            select(SQLOrganization).where(SQLOrganization.slug == slug)
        )
        sql_org = result.scalar_one_or_none()
        return self._map_to_domain(sql_org) if sql_org else None

    async def save(self, organization: Organization) -> Organization:
        sql_org = await self.session.get(SQLOrganization, organization.organization_id)
        if sql_org:
            sql_org.name = organization.name
            sql_org.slug = organization.slug
            sql_org.metadata_json = organization.metadata
            sql_org.updated_at = organization.updated_at
        else:
            sql_org = SQLOrganization(
                organization_id=organization.organization_id,
                name=organization.name,
                slug=organization.slug,
                metadata_json=organization.metadata,
                created_at=organization.created_at,
                updated_at=organization.updated_at,
            )
            self.session.add(sql_org)

        await self.session.commit()
        await self.session.refresh(sql_org)
        return self._map_to_domain(sql_org)

    async def list_all(self) -> List[Organization]:
        result = await self.session.execute(select(SQLOrganization))
        return [self._map_to_domain(o) for o in result.scalars().all()]

    def _map_to_domain(self, sql_org: SQLOrganization) -> Organization:
        return Organization(
            organization_id=sql_org.organization_id,
            name=sql_org.name,
            slug=sql_org.slug,
            created_at=sql_org.created_at,
            updated_at=sql_org.updated_at,
            metadata=sql_org.metadata_json,
        )


class SQLTenantRepository(TenantRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        result = await self.session.execute(
            select(SQLTenant).where(SQLTenant.tenant_id == tenant_id)
        )
        sql_tenant = result.scalar_one_or_none()
        return self._map_to_domain(sql_tenant) if sql_tenant else None

    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        result = await self.session.execute(
            select(SQLTenant).where(SQLTenant.slug == slug)
        )
        sql_tenant = result.scalar_one_or_none()
        return self._map_to_domain(sql_tenant) if sql_tenant else None

    async def list_by_organization(self, organization_id: str) -> List[Tenant]:
        result = await self.session.execute(
            select(SQLTenant).where(SQLTenant.organization_id == organization_id)
        )
        return [self._map_to_domain(t) for t in result.scalars().all()]

    async def save(self, tenant: Tenant) -> Tenant:
        sql_tenant = await self.session.get(SQLTenant, tenant.tenant_id)
        if sql_tenant:
            sql_tenant.name = tenant.name
            sql_tenant.slug = tenant.slug
            sql_tenant.status = tenant.status
            sql_tenant.dedicated_db = tenant.dedicated_db
            sql_tenant.dedicated_vector_index = tenant.dedicated_vector_index
            sql_tenant.settings = tenant.settings
            sql_tenant.updated_at = tenant.updated_at
        else:
            sql_tenant = SQLTenant(
                tenant_id=tenant.tenant_id,
                organization_id=tenant.organization_id,
                name=tenant.name,
                slug=tenant.slug,
                status=tenant.status,
                dedicated_db=tenant.dedicated_db,
                dedicated_vector_index=tenant.dedicated_vector_index,
                settings=tenant.settings,
                created_at=tenant.created_at,
                updated_at=tenant.updated_at,
            )
            self.session.add(sql_tenant)

        await self.session.commit()
        await self.session.refresh(sql_tenant)
        return self._map_to_domain(sql_tenant)

    def _map_to_domain(self, sql_tenant: SQLTenant) -> Tenant:
        return Tenant(
            tenant_id=sql_tenant.tenant_id,
            organization_id=sql_tenant.organization_id,
            name=sql_tenant.name,
            slug=sql_tenant.slug,
            status=sql_tenant.status,
            created_at=sql_tenant.created_at,
            updated_at=sql_tenant.updated_at,
            dedicated_db=sql_tenant.dedicated_db,
            dedicated_vector_index=sql_tenant.dedicated_vector_index,
            settings=sql_tenant.settings,
        )


class SQLWorkspaceRepository(WorkspaceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, workspace_id: str) -> Optional[Workspace]:
        result = await self.session.execute(
            select(SQLWorkspace).where(SQLWorkspace.workspace_id == workspace_id)
        )
        sql_ws = result.scalar_one_or_none()
        return self._map_to_domain(sql_ws) if sql_ws else None

    async def list_by_tenant(self, tenant_id: str) -> List[Workspace]:
        result = await self.session.execute(
            select(SQLWorkspace).where(SQLWorkspace.tenant_id == tenant_id)
        )
        return [self._map_to_domain(w) for w in result.scalars().all()]

    async def save(self, workspace: Workspace) -> Workspace:
        sql_ws = await self.session.get(SQLWorkspace, workspace.workspace_id)
        if sql_ws:
            sql_ws.name = workspace.name
            sql_ws.description = workspace.description
            sql_ws.is_default = workspace.is_default
            sql_ws.metadata_json = workspace.metadata
            sql_ws.updated_at = workspace.updated_at
        else:
            sql_ws = SQLWorkspace(
                workspace_id=workspace.workspace_id,
                tenant_id=workspace.tenant_id,
                name=workspace.name,
                description=workspace.description,
                is_default=workspace.is_default,
                metadata_json=workspace.metadata,
                created_at=workspace.created_at,
                updated_at=workspace.updated_at,
            )
            self.session.add(sql_ws)

        await self.session.commit()
        await self.session.refresh(sql_ws)
        return self._map_to_domain(sql_ws)

    async def delete(self, workspace_id: str) -> bool:
        sql_ws = await self.session.get(SQLWorkspace, workspace_id)
        if sql_ws:
            await self.session.delete(sql_ws)
            await self.session.commit()
            return True
        return False

    def _map_to_domain(self, sql_ws: SQLWorkspace) -> Workspace:
        return Workspace(
            workspace_id=sql_ws.workspace_id,
            tenant_id=sql_ws.tenant_id,
            name=sql_ws.name,
            description=sql_ws.description,
            is_default=sql_ws.is_default,
            created_at=sql_ws.created_at,
            updated_at=sql_ws.updated_at,
            metadata=sql_ws.metadata_json,
        )


class SQLMembershipRepository(MembershipRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: str, tenant_id: str) -> Optional[Membership]:
        result = await self.session.execute(
            select(SQLMembership).where(
                SQLMembership.user_id == user_id,
                SQLMembership.tenant_id == tenant_id
            )
        )
        sql_m = result.scalar_one_or_none()
        return self._map_to_domain(sql_m) if sql_m else None

    async def list_by_user(self, user_id: str) -> List[Membership]:
        result = await self.session.execute(
            select(SQLMembership).where(SQLMembership.user_id == user_id)
        )
        return [self._map_to_domain(m) for m in result.scalars().all()]

    async def list_by_tenant(self, tenant_id: str) -> List[Membership]:
        result = await self.session.execute(
            select(SQLMembership).where(SQLMembership.tenant_id == tenant_id)
        )
        return [self._map_to_domain(m) for m in result.scalars().all()]

    async def save(self, membership: Membership) -> Membership:
        sql_m = await self.session.get(SQLMembership, (membership.user_id, membership.tenant_id))
        if sql_m:
            sql_m.role = membership.role
            sql_m.is_active = membership.is_active
        else:
            sql_m = SQLMembership(
                user_id=membership.user_id,
                tenant_id=membership.tenant_id,
                role=membership.role,
                joined_at=membership.joined_at,
                is_active=membership.is_active,
            )
            self.session.add(sql_m)

        await self.session.commit()
        await self.session.refresh(sql_m)
        return self._map_to_domain(sql_m)

    async def delete(self, user_id: str, tenant_id: str) -> bool:
        sql_m = await self.session.get(SQLMembership, (user_id, tenant_id))
        if sql_m:
            await self.session.delete(sql_m)
            await self.session.commit()
            return True
        return False

    def _map_to_domain(self, sql_m: SQLMembership) -> Membership:
        return Membership(
            user_id=sql_m.user_id,
            tenant_id=sql_m.tenant_id,
            role=sql_m.role,
            joined_at=sql_m.joined_at,
            is_active=sql_m.is_active,
        )
