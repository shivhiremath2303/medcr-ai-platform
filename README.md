# MEDCR AI Platform

![CI](https://github.com/user/repo/actions/workflows/ci.yml/badge.svg)
![Quality](https://github.com/user/repo/actions/workflows/quality.yml/badge.svg)
![Security](https://github.com/user/repo/actions/workflows/security.yml/badge.svg)
![Docker](https://github.com/user/repo/actions/workflows/docker.yml/badge.svg)

## Multi-Evidence & Multi-Defendant Conflict Resolver

An enterprise-grade AI platform for legal investigation assistance using:

- Legal NLP
- Multi-Agent AI
- Knowledge Graphs
- Hybrid RAG
- Explainable AI
- Conflict Detection
- Timeline Reconstruction

## Tech Stack

- **Backend:** Python, FastAPI
- **AI/ML:** PyTorch, Hugging Face, Sentence-Transformers
- **Databases:** PostgreSQL, MongoDB, Neo4j
- **Vector Search:** Qdrant, FAISS
- **Cache:** Redis
- **DevOps:** Docker

## Project Status

✅ **Milestone 6.1: Dependency Injection** - COMPLETE
✅ **Milestone 6.2: Infrastructure Layer** - COMPLETE
✅ **Milestone 6.3: Repository Implementations** - COMPLETE
✅ **Milestone 6.4: Production Configuration** - COMPLETE
✅ **Milestone 6.5: Production Observability** - COMPLETE
✅ **Milestone 6.6: Production Security** - COMPLETE
✅ **Milestone 6.7: Production Persistence & Scalability** - COMPLETE
✅ **Milestone 7.1: Legal Citation & Evidence Engine** - COMPLETE
✅ **Milestone 7.2: Grounding & Hallucination Detection** - COMPLETE
✅ **Milestone 7.3: Advanced Legal Retrieval Intelligence** - COMPLETE
✅ **Milestone 7.4: Multi-Agent Legal Reasoning & Cross-Document Synthesis** - COMPLETE
✅ **Milestone 7.5: AI Evaluation & Benchmarking Framework** - COMPLETE
✅ **Milestone 8.1: Production Dockerization & Containerization** - COMPLETE
✅ **Milestone 8.2: Production CI/CD & Supply Chain Security** - COMPLETE
✅ **Milestone 8.3: Production Scaling & Kubernetes** - COMPLETE
✅ **Milestone 8.4: Production Monitoring, Telemetry & Operations** - COMPLETE
✅ **Milestone 8.5: Final Production Audit & Launch** - COMPLETE
✅ **Milestone 10.1.1: Enterprise HTTP/API Security** - COMPLETE
✅ **Milestone 10.1.2: Authentication Hardening** - COMPLETE
✅ **Milestone 10.1.3: Authorization Hardening** - COMPLETE
✅ **Milestone 10.1.4: Secrets Management** - COMPLETE
✅ **Milestone 10.1.5: Audit Logging** - COMPLETE
✅ **Milestone 10.1.6: API Protection** - COMPLETE
✅ **Milestone 10.1.7: Frontend Security** - COMPLETE
✅ **Milestone 10.1.8: Dependency Security** - COMPLETE

🚀 **Platform Status: PRODUCTION READY**

## Architecture

The project follows **Clean Architecture** and **SOLID** principles:

- **Domain Layer:** Pure business logic and repository interfaces.
- **Application Layer:** Use cases and services (depends only on interfaces).
- **Infrastructure Layer:** Adapters for external libraries (LangChain, FAISS, Google Gemini).
- **API Layer:** FastAPI routes and schemas.

## Containerization

The platform is fully containerized for production deployment.

### Quick Start with Docker

```bash
# Start in production mode
docker-compose up --build -d

# Start in development mode
docker-compose -f docker-compose.dev.yml up --build
```

For more details, see [docker-README.md](docker-README.md).

### Quick Start with Kubernetes (Helm)

```bash
helm install legal-ai ./k8s/helm/legal-ai -n legal-ai --create-namespace
```

For more details, see [k8s/README.md](k8s/README.md).
