# Runbook: High LLM Failure Rate

## Symptoms
* Alert: `LLMFailureRate`
* User reports: "AI not responding" or "Internal Server Error" on RAG queries.
* Logs showing `LLM request failed`.

## Diagnosis
1. Check Google Gemini status page.
2. Verify API Key: Ensure `GEMINI_API_KEY` is valid and hasn't hit quota limits.
3. Check backend logs for specific error messages from the Google GenAI SDK (e.g., 429 Too Many Requests, 500 Internal Error).

## Mitigation
1. **Quota Issue**: If 429 is received, check if someone is abusing the API. Adjust rate limits in `ConfigMap` if necessary.
2. **API Key Change**: If the key is revoked, update the Kubernetes Secret:
   ```bash
   kubectl create secret opaque legal-ai-secrets --from-literal=GEMINI_API_KEY=new-key --dry-run=client -o yaml | kubectl apply -f -
   ```
3. **Model Switch**: If a specific model version is failing, update `gemini_model` in `values.yaml` and redeploy.
