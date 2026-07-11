# MEDCR AI Platform

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

🚧 Under Development: Milestone 8.2 (Relational Persistence & PostgreSQL)

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
