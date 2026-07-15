# Legal AI Platform: Operational Runbook Master Index

This document maps monitoring alerts to remediation procedures.

## Service Level Objectives (SLOs)
*   **Availability**: 99.9% success rate (HTTP 2xx/3xx/4xx).
*   **Latency**: 95% of requests under 2 seconds.
*   **AI Quality**: Grounding score > 0.7 for 90% of requests.

---

## 1. API & Performance Alerts
| Alert Name | Severity | Runbook Link |
|------------|----------|--------------|
| `APIHighErrorRate` | Critical | [LLM Failure Runbook](./runbook-llm-failure.md) |
| `APIHighLatency` | Warning | Check for DB/VectorStore load |
| `ErrorBudgetCritical` | Critical | Freeze non-essential deployments |

## 2. AI & RAG Alerts
| Alert Name | Severity | Runbook Link |
|------------|----------|--------------|
| `LLMServiceDegradation` | Critical | [LLM Failure Runbook](./runbook-llm-failure.md) |
| `AIQualityDrop` | Warning | [AI Quality Runbook](./runbook-ai-quality.md) |
| `AICostSpike` | Critical | Check for runaway background tasks or loops |

## 3. Infrastructure & Capacity Alerts
| Alert Name | Severity | Runbook Link |
|------------|----------|--------------|
| `RedisConnectivityLost` | Critical | [Redis Failure Runbook](./runbook-redis-failure.md) |
| `PodMemorySaturation` | Warning | Increase RAM limits in Helm or check for leaks |
| `HPAAtMaxCapacity` | Warning | Scale up Node group or optimize performance |
| `VectorStoreSaturation` | Warning | Plan for FAISS index sharding |

## 4. Security Alerts
| Alert Name | Severity | Runbook Link |
|------------|----------|--------------|
| `BruteForceAttempt` | Critical | Block IP in WAF/Ingress |
| `ExcessiveAccountLockouts` | Warning | Audit auth logs for specific usernames |
