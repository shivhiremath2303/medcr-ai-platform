# Production Checklists

## 1. Pre-Deployment Checklist
- [ ] All unit and integration tests are passing in CI.
- [ ] Security scans (Trivy, pip-audit) show no Critical/High vulnerabilities.
- [ ] `GEMINI_API_KEY` is configured in Kubernetes Secrets.
- [ ] Resource quotas are defined for the target namespace.
- [ ] Database/Redis connectivity is verified.

## 2. Deployment Checklist
- [ ] `helm install` or `helm upgrade` executed.
- [ ] Verify pods are in `Running` state: `kubectl get pods -n legal-ai`.
- [ ] Check health endpoint: `curl https://legal-ai.local/health/ready`.
- [ ] Verify Ingress routing: `curl https://legal-ai.local/api/v1/health`.
- [ ] Confirm metrics are being scraped by Prometheus.

## 3. Post-Deployment Checklist
- [ ] Run a smoke test (upload a sample document and query it).
- [ ] Monitor error rates in Grafana for 15 minutes.
- [ ] Check for memory leaks or CPU spikes.
- [ ] Verify logs for any `CRITICAL` or `ERROR` messages.

## 4. Incident Response Checklist
- [ ] **Identify**: What is the symptom? (e.g., 500 errors, latency).
- [ ] **Isolate**: Is it the Backend, Redis, or an external API (Gemini)?
- [ ] **Mitigate**: Can we rollback? Can we restart pods?
- [ ] **Resolve**: Fix the root cause.
- [ ] **Post-Mortem**: Document the incident and prevent recurrence.
