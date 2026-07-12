# Capacity Planning

## 1. Resource Estimates

| Component | Users | Storage | CPU (Req/Lim) | RAM (Req/Lim) |
| :--- | :--- | :--- | :--- | :--- |
| **Small** | < 10 | 10 GB | 1 / 2 | 2 GB / 4 GB |
| **Medium** | 10 - 50 | 50 GB | 4 / 8 | 8 GB / 16 GB |
| **Large** | 50+ | 200 GB+ | 16+ / 32+ | 32 GB+ / 64 GB+ |

## 2. Scaling Factors

### Redis (Memory)
- **Session Data**: ~50 KB per active session.
- **Cache**: 1 GB is sufficient for ~1000 legal document chunks.
- **Recommendation**: Scale RAM based on the number of concurrent active conversations.

### FAISS (Memory/Storage)
- **Index Size**: ~1 MB per 1000 chunks (using `all-MiniLM-L6-v2`).
- **Growth**: Linear with the number of documents uploaded.
- **Limitation**: FAISS indexes are currently stored on disk but loaded into RAM. Ensure `backend` RAM > 2x Index Size.

### Storage
- **Uploads**: ~2 MB per PDF (Average).
- **Metadata**: ~10 KB per document.
- **Growth**: ~2.5 GB per 1000 documents.

## 3. LLM Costs (Gemini)
- **Input**: ~$0.125 / 1M tokens (Gemini 2.0 Flash).
- **Output**: ~$0.375 / 1M tokens.
- **Average Query**: ~2000 input tokens + 500 output tokens = ~$0.0004 per query.
