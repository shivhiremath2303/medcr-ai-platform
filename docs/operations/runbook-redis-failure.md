# Runbook: Redis Failure

## Symptoms
* Alert: `RedisDown`
* API errors (500) for session management, rate limiting, and caching.
* Logs showing `ConnectionError: Error connecting to redis`.

## Diagnosis
1. Check Redis pod status:
   ```bash
   kubectl get pods -l app=redis -n legal-ai
   ```
2. Check Redis logs:
   ```bash
   kubectl logs -l app=redis -n legal-ai
   ```
3. Verify connectivity from backend:
   ```bash
   kubectl exec -it <backend-pod> -n legal-ai -- redis-cli -h legal-ai-redis ping
   ```

## Mitigation
1. **Restart Redis**:
   ```bash
   kubectl rollout restart deployment legal-ai-redis -n legal-ai
   ```
2. **Check PVC**: If Redis fails to start, verify the PersistentVolume is not full or corrupted.
3. **Fallback**: The application should automatically fallback to in-memory repositories if Redis is unavailable (verify in logs), but performance will be degraded and sessions lost.
