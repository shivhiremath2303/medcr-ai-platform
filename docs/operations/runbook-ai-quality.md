# Runbook: AI Quality Degradation (`AIQualityDrop`)

## Symptoms
*   `AIQualityDrop` alert firing in Prometheus.
*   Grounding scores in Grafana "AI Intelligence" dashboard trending below 0.7.
*   User reports of hallucinations or incorrect citations.

## Diagnostics
1.  **Check Retrieval Performance**: Look at "Retrieval NDCG" in the AI Dashboard. If low, the issue is with the Vector Store or Reranker.
2.  **Verify LLM Version**: Check if a model update (e.g., Gemini 2.0 Flash) introduced changes in prompt adherence.
3.  **Inspect Hallucination Metrics**: High contradiction rates usually point to the LLM ignoring context.
4.  **Sample Traces**: Open Jaeger/Tempo and search for traces with `grounding_score < 0.5`. Review the `llm.prompt` and `llm.response`.

## Mitigation
1.  **Revert Prompt Changes**: If the prompt was recently modified, revert to the last stable version.
2.  **Tune Retrieval Parameters**: Increase `top_k` or adjust the `hybrid_weight_vector` in settings.
3.  **Clear Cache**: If the issue is localized to specific documents, verify if the FAISS index needs to be rebuilt.
4.  **Escalate**: If metrics don't improve, escalate to the AI/Data Science team.
