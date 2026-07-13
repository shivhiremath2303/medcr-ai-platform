# Enterprise Load Testing Guide

This document outlines how to perform AI-specific load testing on the Legal AI Platform using `k6`.

## Prerequisites
*   Install k6: `brew install k6` or `choco install k6`
*   Configure target environment: `export BASE_URL=https://api.medcr.ai`
*   Obtain a valid test token: `export API_TOKEN=your_jwt_token`

## Test Scenarios

### 1. RAG Benchmark (`rag_benchmark.js`)
*   **Goal**: Test end-to-end RAG pipeline (Retrieval + Generation + Evaluation).
*   **Simulates**: Concurrent users asking legal questions.
*   **Command**: `k6 run -e BASE_URL=$BASE_URL -e API_TOKEN=$API_TOKEN tests/load/rag_benchmark.js`

### 2. Ingestion Stress (`ingestion_benchmark.js`)
*   **Goal**: Test background worker throughput and document processing.
*   **Simulates**: Bulk upload of 1,000s of legal documents.
*   **Command**: `k6 run -e BASE_URL=$BASE_URL tests/load/ingestion_benchmark.js`

### 3. Stress & Load Shedding (`stress_test.js`)
*   **Goal**: Verify that `ResourceGuard` correctly rejects tasks when the system is overloaded.
*   **Command**: `k6 run tests/load/stress_test.js`

## Interpreting Results in Grafana

While tests are running, monitor the **"Legal AI Platform Overview"** dashboard:

1.  **AI Request Volume**: Should match k6's `http_reqs`.
2.  **p95 Latency**: Should stay below 5s for RAG and 500ms for health checks.
3.  **Circuit Breaker Status**: If Gemini API errors occur, watch for `resilience_circuit_tripped_total`.
4.  **Resource Usage**: Monitor `resource_memory_ratio`. If it hits 0.85, verify if `Load Shedding` logs appear in the backend.

## Capacity Report Template

| Metric | Target | Result (at 50 VUs) | Pass/Fail |
|--------|--------|---------------------|-----------|
| RAG Latency (p95) | < 5s | | |
| Ingestion Throughput| > 2 docs/sec | | |
| Error Rate | < 1% | | |
| Recovery Time | < 60s | | |
