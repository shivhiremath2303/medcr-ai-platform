# Task List: Phase 10.4 Enterprise Multi-Tenant Architecture

## 10.4.1 Tenant Domain & SQL Models
- [x] Create `backend/app/database/models/tenant_sql.py` with SQLAlchemy models
- [x] Refine `backend/app/domain/models/tenant.py` for persistence compatibility

## 10.4.2 Tenant Repositories
- [x] Implement `SQLOrganizationRepository`
- [x] Implement `SQLTenantRepository`
- [x] Implement `SQLWorkspaceRepository`
- [x] Implement `SQLMembershipRepository`
- [x] Update `backend/app/di.py` to use SQL repositories

## 10.4.3 Tenant Authentication
- [x] Update `AuthService` for SQL membership validation
- [x] Implement tenant context switching in `AuthService`

## 10.4.4 Metadata & File Isolation
- [x] Update `FilesystemDocumentRepository` to be tenant-aware
- [x] Verify `LocalStorageAdapter` tenant isolation

## 10.4.5 Vector & Cache Isolation
- [x] Update `FAISSVectorRepository` for strict tenant filtering
- [x] Update `RAGService` to include `tenant_id` in all cache keys
- [x] Update `RedisConversationRepository` for tenant isolation

## 10.4.6 Multi-Tenant Integration & Testing
- [x] Update `init_dev_user` for SQL persistence
- [x] Add E2E tests for tenant isolation

## 10.4.7 Tenant-aware Metrics & Observability
- [x] Update `MetricsRegistry` to automatically inject `tenant_id` labels
- [x] Add `tenant_id` to `context.py` and propagate from JWT middleware
