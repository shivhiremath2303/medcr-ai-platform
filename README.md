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

🚧 Under Development: Milestone 6.4 (Production Hardening)

## Architecture

The project follows **Clean Architecture** and **SOLID** principles:

- **Domain Layer:** Pure business logic and repository interfaces.
- **Application Layer:** Use cases and services (depends only on interfaces).
- **Infrastructure Layer:** Adapters for external libraries (LangChain, FAISS, Google Gemini).
- **API Layer:** FastAPI routes and schemas.
