# ADR 0002: Hybrid Retrieval with BM25 and Vector Search

## Status
Accepted

## Context
Legal documents often contain specific terminology and clause numbers that semantic (vector) search might miss. Conversely, keyword search (BM25) fails on semantic meaning and synonyms.

## Decision
We implemented a **Hybrid Retrieval** strategy:
1.  **Vector Search (FAISS)**: Captures semantic context and meaning.
2.  **BM25 (Keyword Search)**: Captures exact legal terminology and citations.
3.  **Reciprocal Rank Fusion (RRF) / Weighting**: Combines results from both methods.
4.  **Cross-Encoder Reranking**: Re-evaluates the top candidates for maximum relevance.

## Alternatives Considered
- **Vector-only Search**: Fast but missed exact matches for legal citations.
- **Elasticsearch/OpenSearch**: Powerful but increased infrastructure footprint.

## Tradeoffs
- **Latency**: Running two searches and a reranker is slower than a single search.
- **Resource Usage**: Requires indexing data in two different formats.

## Consequences
- **Accuracy**: Significantly improved retrieval recall for specific legal queries.
- **Reliability**: Better grounding as the model receives more relevant context.
