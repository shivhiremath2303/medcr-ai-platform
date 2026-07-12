# SLOs & SLIs for Legal AI Platform

This document defines the Service Level Objectives (SLOs) and Service Level Indicators (SLIs) for the production platform.

## 1. Availability

*   **SLI**: Percentage of successful HTTP requests (non-5xx) over a 30-day window.
*   **SLO**: 99.9% availability.
*   **Measurement**: `sum(rate(http_requests_total{status!~"5.."}[30d])) / sum(rate(http_requests_total[30d]))`

## 2. Latency (API)

*   **SLI**: 95th percentile latency for RAG queries.
*   **SLO**: 95% of queries completed within 10 seconds.
*   **Measurement**: `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{path="/api/v1/rag/query"}[30d])) by (le))`

## 3. Retrieval Performance

*   **SLI**: Average retrieval latency.
*   **SLO**: < 2 seconds.
*   **Measurement**: `avg(retrieval_duration_seconds)`

## 4. AI Quality (Grounding)

*   **SLI**: Average grounding score from evaluation engine.
*   **SLO**: > 0.8 (no hallucinations).
*   **Measurement**: `avg(evaluation_scores{metric="grounding"})`

## 5. Cache Efficiency

*   **SLI**: Cache hit ratio.
*   **SLO**: > 40% for recurring legal document lookups.
*   **Measurement**: `sum(rate(cache_requests_total{status="hit"}[1h])) / sum(rate(cache_requests_total[1h]))`
