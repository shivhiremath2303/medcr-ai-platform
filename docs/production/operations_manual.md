# Operations Manual

## 1. Monitoring and Health
The platform exposes several endpoints for operational visibility:
- **Liveness**: `/health/live`
- **Readiness**: `/health/ready`
- **Metrics**: `/metrics` (Prometheus format)

## 2. Scaling
### Horizontal Scaling
The Backend is configured with a **Horizontal Pod Autoscaler (HPA)**.
- Trigger: 80% CPU Utilization.
- Minimum Replicas: 2
- Maximum Replicas: 10

To manually scale:
```bash
kubectl scale deployment legal-ai-backend --replicas=5 -n legal-ai
```

### Vertical Scaling
If memory usage is high (due to FAISS index size), update `values.yaml`:
```yaml
backend:
  resources:
    limits:
      memory: 4Gi
```

## 3. Maintenance

### Log Inspection
```bash
kubectl logs -f -l app=backend -n legal-ai
```

### Clearing Cache
To clear the Redis cache manually:
```bash
kubectl exec -it <redis-pod> -n legal-ai -- redis-cli flushall
```

## 4. Upgrades
The platform uses **Rolling Updates** for zero-downtime deployments.
```bash
helm upgrade legal-ai ./k8s/helm/legal-ai -f my-values.yaml -n legal-ai
```

## 5. Rollbacks
If a deployment fails:
```bash
helm rollback legal-ai <revision-number> -n legal-ai
```
