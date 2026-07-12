# ADR 0003: Redis for Caching and Session Management

## Status
Accepted

## Context
The platform needs a high-performance, distributed store for rate limiting, conversation memory, and token revocation.

## Decision
We chose **Redis** as our primary persistence and caching layer for non-document data.
- **Rate Limiting**: Uses Redis fixed-window counters.
- **Conversation Memory**: Stores history with TTL.
- **Token Revocation**: Stores blacklisted JWT IDs.
- **Cache**: Stores expensive retrieval and reasoning results.

## Alternatives Considered
- **In-Memory (Python Dicts)**: Not scalable across multiple replicas.
- **PostgreSQL**: Slower for frequent small writes (rate limiting).

## Tradeoffs
- **Infrastructure Overhead**: Requires a separate running service (Deployment/Service).
- **Data Volatility**: While Redis has persistence, it's primarily an in-memory store.

## Consequences
- **Scalability**: Backend replicas can share state via Redis.
- **Performance**: Sub-millisecond latency for session and rate limit checks.
