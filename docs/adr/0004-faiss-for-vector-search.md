# ADR 0004: FAISS for Local Vector Search

## Status
Accepted

## Context
A legal RAG system requires efficient similarity search over document embeddings. For the initial production release, we want to minimize cloud-specific dependencies and maintain high speed.

## Decision
We chose **FAISS (Facebook AI Similarity Search)** as our vector search engine.
- **Index Type**: Flat L2 or HNSW (depending on document volume).
- **Storage**: Indexes are persisted to disk and loaded into memory on startup.

## Alternatives Considered
- **Pinecone**: Easy to use but cloud-dependent and costs money.
- **Qdrant / Milvus**: Powerful but significantly more complex to deploy and maintain in a small-to-medium scale environment.

## Tradeoffs
- **Scale**: FAISS is a library, not a database. It works well up to millions of vectors but lacks native clustering/sharding.
- **Dynamic Updates**: Adding documents requires re-saving the index file.

## Consequences
- **Low Latency**: In-memory search is extremely fast.
- **Cost**: No additional licensing or cloud costs.
- **Simplicity**: No complex database cluster to manage; just a file on a Persistent Volume.
