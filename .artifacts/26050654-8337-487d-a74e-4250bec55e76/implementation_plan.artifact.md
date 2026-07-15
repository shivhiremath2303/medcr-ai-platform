# Implementation Plan: Phase 10.4 Enterprise Multi-Tenant Architecture

This phase evolves the platform into a SaaS-ready architecture with strict tenant isolation, scalable repository patterns, and tenant-aware AI pipelines.

## User Review Required

> [!IMPORTANT]
> **Database Transition**: This phase will transition from Memory-based Tenant/Organization repositories to Persistent SQL-based repositories (PostgreSQL/SQLite). Existing "default" data will be migrated to the database.

> [!WARNING]
> **Cache Invalidation**: Deployment of multi-tenant cache isolation will invalidate current global caches to prevent data leakage.

## Proposed Changes

### [Component] Tenant Domain & Persistence
Migrate Tenant models to SQLAlchemy and implement persistent repositories.

#### [MODIFY] [tenant.py](file:///C:/Users/LENOVO/medcr-ai-platform/backend/app/domain/models/tenant.py)
- Refine Pydantic models for persistence.

#### [NEW] [tenant_sql.py](file:///C:/Users/LENOVO/medcr-ai-platform/backend/app/database/models/tenant_sql.py)
- SQLAlchemy models for Organization, Tenant, Workspace, Membership.

#### [NEW] [sql_tenant_repository.py](file:///C:/Users/LENOVO/medcr-ai-platform/backend/app/infrastructure/storage/sql_tenant_repository.py)
- Production-ready implementation of `TenantRepository`, `OrganizationRepository`, etc.

---

### [Component] Authentication & Authorization
Enhance JWT claims and session management to support multi-tenant context.

#### [MODIFY] [auth_service.py](file:///C:/Users/LENOVO/medcr-ai-platform/backend/app/core/security/auth_service.py)
- Support tenant validation during login.
- Support switching active tenant context for users with multiple memberships.

#### [MODIFY] [dependencies.py](file:///C:/Users/LENOVO/medcr-ai-platform/backend/app/core/security/dependencies.py)
- Strict `tenant_id` validation in `get_current_user`.

---

### [Component] Tenant-aware AI Pipeline
Isolate retrieval and caching by tenant context.

#### [MODIFY] [faiss_repository.py](file:///C:/Users/LENOVO/medcr-ai-platform/backend/app/infrastructure/vectorstore/faiss_repository.py)
- Prepare for index sharding (One FAISS index per tenant or strict metadata partitioning).

#### [MODIFY] [rag_service.py](file:///C:/Users/LENOVO/medcr-ai-platform/backend/app/services/rag/rag_service.py)
- Inject `tenant_id` into all cache key generation logic.

---

### [Component] Infrastructure & Integration
Wire new repositories and update initialization logic.

#### [MODIFY] [di.py](file:///C:/Users/LENOVO/medcr-ai-platform/backend/app/di.py)
- Switch from `MemoryTenantRepository` to `SQLTenantRepository`.

## Verification Plan

### Automated Tests
- `pytest tests/tenant_isolation/`: New test suite to verify no data leakage between `tenant_a` and `tenant_b`.
- `pytest tests/persistence/`: Verify Tenant/Organization CRUD in SQL.

### Manual Verification
- Login as a user belonging to two organizations and verify ability to switch contexts.
- Upload documents to Tenant A and verify they are invisible to Tenant B's RAG queries.

## Milestones
- **10.4.1**: Tenant Domain & SQL Models
- **10.4.2**: SQL Repositories Implementation
- **10.4.3**: Tenant-aware Authentication
- **10.4.4**: Metadata & File Isolation
- **10.4.5**: Vector & Cache Isolation
- **10.4.6**: Multi-Tenant Integration & Testing
