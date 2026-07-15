# Architectural Audit: Enterprise Legal AI Platform

This document provides a comprehensive audit of the current platform architecture as a baseline for Phase 10.4 (Multi-Tenant Evolution).

## 1. Current Architecture
The platform follows **Clean Architecture** and **Domain-Driven Design (DDD)** principles.
- **Layers**: API (FastAPI) -> Services -> Domain (Models/Repository Interfaces) -> Infrastructure (Adapters).
- **Inversion of Control**: Dependencies are managed in `app/di.py` (Composition Root) and injected via FastAPI's `Depends`.
- **Patterns**: Repository Pattern, Adapter Pattern, Singleton for core infrastructure (FAISS, Redis client).

## 2. Current Dependency Graph
- **Core**: `Settings`, `Logger`, `Telemetry`.
- **Security**: `JWTManager` -> `AuthService` -> `AuthorizationService`.
- **Storage**: `StorageProvider` (Local FS) -> `DocumentRepository` (JSON FS) -> `VectorStoreRepository` (FAISS).
- **AI**: `EmbeddingRepository` (HuggingFace) -> `LLMProvider` (Gemini) -> `RAGService`.
- **Transport**: FastAPI -> Middleware (Observability, Security) -> Routers.

## 3. Current Authentication Model
- **Mechanism**: OAuth2 Password Flow + JWT.
- **Tokens**: Access Token (30m) + Refresh Token (7d) with rotation.
- **Session Management**: Session ID (`sid`) stored in JWT and tracked in Redis for revocation.
- **Identity**: `CurrentUser` abstraction injected into routes.

## 4. Current Authorization Model
- **Type**: RBAC (Role-Based Access Control) with granular permissions.
- **Permissions**: Defined in `Permission` enum (e.g., `document:read`).
- **Policy Enforcement**: `AuthorizationService` performs permission checks and resource ownership verification (`owner_id` matching).

## 5. Current Repository Structure
- **Domain**: Interfaces in `app/domain/repositories/`.
- **Infrastructure**: Implementations in `app/infrastructure/storage/`, `app/infrastructure/vectorstore/`, etc.
- **In-Memory**: Several repositories (Tenant, Membership) currently use `Memory` implementations in `di.py`.

## 6. Current Storage Model
- **Documents**: Physical files in `uploads/documents/`. Metadata in `data/metadata/*.json`.
- **Vectors**: FAISS index persisted as `legal_documents.faiss`.
- **Transient**: Redis for sessions, rate limiting, and cache.

## 7. Current Document Ownership Model
- `Document` model contains `owner_id` (User) and `tenant_id`.
- Access is restricted by `AuthorizationService.can_access_document`.

## 8. Current AI Pipeline
- **Ingestion**: `DocumentService` -> Parser -> Chunker -> Vector Store (Incremental Add).
- **RAG**: `RAGService` -> Query Rewriter -> Hybrid Retriever -> Context Builder -> Gemini LLM -> Grounding Engine -> Reasoning Engine -> Evaluation.

## 9. Current Caching Strategy
- **Multi-Level**: L1 (In-memory LRU) + L2 (Redis).
- **Namespacing**: `cache:{key}`. Key is a hash of inputs (query, k, context).

## 10. Current Conversation Storage
- **Provider**: `RedisConversationRepository`.
- **Key**: `conv:{user_id}`.
- **Constraint**: Fixed window of messages (L-TRIM).

## 11. Current Audit Logging
- **Service**: `AuditService`.
- **Sink**: Structured JSON Logs (`security.audit` logger).
- **Events**: Auth, Authz, Document, AI operations.

## 12. Current API Design
- **RESTful**: Resource-based paths (`/api/v1/documents`, `/api/v1/rag`).
- **Dependencies**: Per-route rate limiting and permission checking.
- **Streaming**: Supports SSE for RAG responses.

## 13. Current Frontend Architecture
- **Framework**: Next.js 15 (App Router), React 19, TypeScript.
- **UI**: Tailwind CSS + shadcn/ui.
- **Structure**: Feature-based (`frontend/src/features/`).

## 14. Current Deployment Architecture
- **Containerization**: Docker (Multi-stage builds).
- **Orchestration**: Docker Compose (Dev/Test) and Kubernetes (Helm) for Production.
- **Infrastructure**: Backend (Python/FastAPI) + Redis.

## 15. Current CI/CD Pipeline
- **Workflow**: GitHub Actions.
- **Gates**: Linting (Ruff), Security (Gitleaks), Testing (Pytest with 133+ tests), Coverage (50% threshold).

---

# Multi-Tenant Readiness Assessment

| Area | Risk Level | Issue | Impact |
| :--- | :--- | :--- | :--- |
| **Authentication** | Low | `init_dev_user` hardcodes `tenant-default`. | Not SaaS-ready for dynamic signup. |
| **Authorization** | Medium | Users are tied to one tenant in JWT. | Multi-membership requires session switching logic. |
| **FAISS Index** | High | Single global FAISS index with logical filtering. | Scaling risk; potential metadata leak if filter fails; index size growth. |
| **Cache Isolation** | High | Global cache keys (`cache:{hash}`). | **Data Leakage Risk**: Different tenants asking same question might get cached answer from another tenant. |
| **Conversation History** | Medium | Keyed by `conv:{user_id}` only. | If `user_id` collisions occur or if a user belongs to multiple tenants, history is mixed. |
| **Background Jobs** | Low | Global Redis queue. | Single tenant could saturate worker capacity (Fairness issue). |
| **Metadata Storage** | Medium | Flat directory `data/metadata/`. | Large number of files in single dir; collision risk if `document_id` isn't unique enough. |
| **Audit Logs** | Low | Global log stream. | Difficult to provide tenant-specific audit exports. |
| **Metrics** | Low | Global Prometheus metrics. | Difficult to perform tenant-specific billing/usage analysis. |

### Detailed Issues

#### 1. Shared Vector Index Risk
Currently, `FAISSVectorRepository` uses a single index for all documents and applies a filter `{"tenant_id": tenant_id}` at search time.
- **Risk**: While logically isolated, a bug in the filter implementation or FAISS metadata handling could leak snippets to another tenant.
- **Scaling**: As tenant count grows, the single index becomes a bottleneck.

#### 2. Cache Key Poisoning
Cache keys are currently `answer:{hash(question, context, k)}`.
- **Critical Issue**: The `tenant_id` is NOT part of the hash in some layers, or the global namespace is shared. If two tenants have a document with similar content, one could see the cached reasoning/answer intended for the other.

#### 3. Hard-coded Resources
- `di.py` defaults to `tenant-default`.
- `init_dev_user` is a setup script that won't scale for automated tenant provisioning.

#### 4. Shared Uploads
- `LocalStorageAdapter` already implements tenant subdirectories (`uploads/{tenant_id}/`), which is a positive sign for physical isolation.

#### 5. Database Isolation
- `database_foundation.py` uses a single `legal_ai.db`.
- SaaS requirements usually demand at least schema-level isolation or strict row-level security (RLS). Currently, only row-level (model-level) `tenant_id` exists.

---
**Recommendation**: Proceed to 10.4.1 Tenant Domain Model and 10.4.2 Tenant Repositories to replace "Memory" implementations with persistent storage (PostgreSQL/SQLAlchemy).
