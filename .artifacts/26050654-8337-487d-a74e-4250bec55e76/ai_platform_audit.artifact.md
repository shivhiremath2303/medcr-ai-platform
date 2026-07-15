# AI Platform Audit: Enterprise Legal AI Platform

This document provides a comprehensive audit of the AI infrastructure as a baseline for Phase 10.5 (Optimization).

## 1. Current AI Architecture
- **Framework**: Clean Architecture with DDD.
- **Providers**: Google Gemini (LLM), HuggingFace (Embeddings/Reranker), FAISS (Vector Store).
- **Inversion of Control**: Managed via `di.py` and `RetrievalService` / `RAGService`.

## 2. Current RAG Pipeline
- **Flow**: `Query Rewriting` -> `Hybrid Retrieval` -> `Reranking` -> `Context Building` -> `LLM Generation` -> `Grounding/Reasoning Extraction` -> `Evaluation`.
- **Status**: Stable but highly sequential. Total latency is dominated by LLM generation and CPU-bound local models.

## 3. Current Retrieval Pipeline
- **Mechanism**: `HybridRetrieverAdapter` runs Vector (FAISS) and Keyword (BM25) search in parallel.
- **Strategy**: Intelligent strategy selection in `RetrievalService` based on query intent (e.g., Clause Lookup vs. Definition).
- **Top-K**: Dynamic Top-K (K=3 to 15) based on query complexity.

## 4. Current Embedding Pipeline
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`.
- **Execution**: Local CPU via `HuggingFaceEmbeddingAdapter`.
- **Scaling**: Offloaded to a thread pool to avoid blocking the event loop.

## 5. Current Reranking Pipeline
- **Model**: `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- **Execution**: Local CPU via `CrossEncoderAdapter`.
- **Latency**: High (CPU-bound inference on multiple pairs).

## 6. Current Prompt Pipeline
- **Template**: `LEGAL_RAG_PROMPT` in `GeminiLLMAdapter`.
- **Style**: Direct instruction with context injection.
- **Optimization**: Minimal. No prompt compression or few-shot tuning.

## 7. Current Grounding Pipeline
- **Mechanism**: `GroundingEngine` uses regex to extract citations and notes from LLM output.
- **Validation**: Post-processing check ensures cited evidence actually exists in retrieval results.
- **Scoring**: Heuristic calculation [0, 1] based on sufficiency and citation accuracy.

## 8. Current Citation Pipeline
- **Mechanism**: `ContextBuilder` labels evidence as `[Evidence N]`.
- **Consistency**: Relies on LLM adhering to instructions to cite correctly.

## 9. Current Evaluation Pipeline
- **Framework**: `EvaluationEngine` computes Precision@K, Recall@K, MRR, nDCG, and grounding accuracy.
- **Reporting**: Generates an `EvaluationReport` for every query, including estimated cost (Gemini rates).

## 10. Current Memory Pipeline
- **Storage**: Redis-backed message list.
- **Window**: Fixed window (default 100 messages) with `L-TRIM`.

## 11. Current AI Latency (Estimates)
- **Understanding**: ~500ms (LLM call).
- **Retrieval**: ~200ms (Parallel FAISS + BM25).
- **Reranking**: ~1000ms+ (CPU inference).
- **Generation**: ~3000ms - 8000ms (Gemini API).
- **Total**: ~5s - 12s per query.

## 12. Current Token Usage
- **Input**: Context (K results) + Query. Typically 2k - 8k tokens.
- **Output**: Detailed legal analysis. Typically 500 - 1500 tokens.

## 13. Current Bottlenecks
- **CPU Inference**: Reranking and Embeddings on CPU are slow and block worker resources.
- **Sequential Pipeline**: Understanding and Retrieval are sequential. Grounding and Reasoning are extracted after full generation.
- **Static Chunking**: 1000-character chunks may break legal clauses mid-sentence.

## 14. Current Scalability Limitations
- **Memory Usage**: FAISS index and local models reside in pod memory.
- **Throughput**: Limited by number of CPU cores and thread pool size for local models.

## 15. Current Operational Costs
- **Gemini 2.0 Flash**: ~$0.10/1M tokens input, ~$0.40/1M tokens output.
- **Efficiency**: No response caching means identical queries incur full costs.

---

# AI Optimization Roadmap (Phase 10.5)

| Milestone | Objective | Strategy |
| :--- | :--- | :--- |
| **10.5.1** | **Retrieval Optimization** | Semantic Chunking & Semantic Cache. |
| **10.5.2** | **Latency Optimization** | Parallelize RAG Analytics & Speculative Retrieval. |
| **10.5.3** | **Context Compression** | Dynamic Prompt Pruning & Context Summarization. |
| **10.5.4** | **Adaptive Reranking** | Threshold-based bypass for high-confidence retrievals. |
| **10.5.5** | **Quality Evaluation** | Automated Benchmarking & Confidence Calibration. |
| **10.5.6** | **Cost Optimization** | Model Routing (Flash for summary, Pro for complex analysis). |
