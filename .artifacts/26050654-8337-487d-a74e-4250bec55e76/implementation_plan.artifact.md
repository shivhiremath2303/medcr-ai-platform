# Implementation Plan: Phase 10.5 Enterprise AI Platform Optimization

This phase focuses on improving the quality, latency, and cost-efficiency of the AI platform while maintaining its stable Clean Architecture.

## User Review Required

> [!IMPORTANT]
> **Performance Improvements**: We are introducing **Parallel Analytics** and **Semantic Caching**. This will significantly reduce perceived latency but will increase Redis memory usage for the cache.

> [!WARNING]
> **Chunking Evolution**: Switching to **Semantic Chunking** will require re-indexing existing documents to take advantage of improved retrieval coherence.

## Proposed Changes

### [Component] Retrieval & Chunking
Improve retrieval coherence and accuracy.

#### [MODIFY] [document_service.py](file:///C:/Users/LENOVO/medcr-ai-platform/backend/app/services/document/document_service.py)
- Integrate **Semantic Chunking** using semantic boundaries instead of fixed character counts.

#### [NEW] [semantic_chunker.py](file:///C:/Users/LENOVO/medcr-ai-platform/backend/app/infrastructure/parser/semantic_chunker.py)
- Implementation of a chunker that uses embedding distances to find natural breaks in legal text.

---

### [Component] Latency & Pipeline
Parallelize non-dependent steps and introduce intelligent caching.

#### [MODIFY] [rag_service.py](file:///C:/Users/LENOVO/medcr-ai-platform/backend/app/services/rag/rag_service.py)
- Implement **Parallel Analytics Extraction**: Extract grounding and reasoning concurrently with the final response construction.
- Introduce **Semantic Retrieval Cache**: Cache retrieval results based on query embedding similarity to handle variations of the same question.

#### [MODIFY] [retrieval_service.py](file:///C:/Users/LENOVO/medcr-ai-platform/backend/app/services/retrieval/retrieval_service.py)
- Implement **Adaptive Reranking**: Skip the heavy CrossEncoder step if initial retrieval confidence is extremely high (e.g., > 0.9).

---

### [Component] Context & Prompt
Optimize token usage and LLM efficiency.

#### [MODIFY] [context_builder.py](file:///C:/Users/LENOVO/medcr-ai-platform/backend/app/services/retrieval/context_builder.py)
- Implement **Dynamic Context Pruning**: Use a lightweight model or heuristic to remove "noise" from chunks before injecting into the main prompt.

#### [MODIFY] [gemini_adapter.py](file:///C:/Users/LENOVO/medcr-ai-platform/backend/app/infrastructure/llm/gemini_adapter.py)
- Support **Model Routing**: Dynamically switch between Gemini 2.0 Flash and Gemini 1.5 Pro based on query complexity.

## Verification Plan

### Automated Tests
- `pytest tests/performance/`: Benchmark latency before and after optimizations.
- `pytest tests/retrieval/`: Compare nDCG scores between static and semantic chunking.

### Manual Verification
- Monitor Prometheus metrics for `ai_latency_seconds` and `ai_tokens_consumed`.
- Verify that "Lost-in-the-middle" issues are mitigated by checking relevance of citations for long contexts.

## Milestones
- **10.5.1**: Retrieval Optimization (Semantic Chunking)
- **10.5.2**: Latency Optimization (Parallel Analytics & Adaptive Reranking)
- **10.5.3**: Context Compression & Prompt Pruning
- **10.5.4**: Semantic Caching & Model Routing
- **10.5.5**: Enterprise Benchmarking & Calibration
