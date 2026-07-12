# ADR 0001: Use of Clean Architecture

## Status
Accepted

## Context
The Legal AI RAG Platform requires high maintainability, testability, and independence from external libraries (LLM providers, Vector Databases). The business logic (legal reasoning, grounding) must be isolated from infrastructure details.

## Decision
We adopted **Clean Architecture** principles. The codebase is organized into layers:
- **Domain Layer**: Pure business logic, entities, and repository interfaces.
- **Application Layer**: Use cases and services that coordinate domain logic.
- **Infrastructure Layer**: Adapters for external services (Google Gemini, FAISS, Redis).
- **API Layer**: FastAPI routes and request/response schemas.

## Alternatives Considered
- **Layered Architecture (MVC)**: Simpler but leads to tight coupling with the database/web framework.
- **Microservices**: Deemed too complex for the initial phase but can be evolved from this structure.

## Tradeoffs
- **Complexity**: Requires more boilerplate code (interfaces, adapters).
- **Learning Curve**: New developers need to understand the separation of concerns.

## Consequences
- **Independence**: We can swap FAISS for Qdrant or Gemini for OpenAI by implementing a new adapter in the infrastructure layer.
- **Testability**: Domain logic can be unit tested without any external dependencies.
- **Stability**: Changes in external APIs (e.g., Google GenAI SDK) only affect a single adapter.
