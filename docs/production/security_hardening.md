# Security Hardening Audit

## 1. Container Hardening
- **Non-Root User**: Backend runs as user `legalai` (UID 999).
- **Read-Only Root FS**: Recommended for production (not yet enforced in Helm).
- **Distroless/Slim Base**: Uses `python:3.12-slim` to minimize attack surface.

## 2. Kubernetes Security
- **Namespace Isolation**: All resources reside in the `legal-ai` namespace.
- **Network Policies**: 
  - Deny all by default (Ingress/Egress).
  - Backend can only talk to Redis and the internet (for Gemini API).
  - Redis only accepts traffic from Backend.
- **RBAC**: No default service account tokens are mounted.

## 3. Secret Management
- **GitHub Secrets**: Used for CI/CD pipelines.
- **Kubernetes Secrets**: Used for runtime environment variables.
- **No Hardcoded Keys**: Audited for `GEMINI_API_KEY` and `JWT_SECRET_KEY`.

## 4. API Security
- **Rate Limiting**: Enforced via Redis.
- **JWT Authentication**: HS256 algorithm with configurable expiration.
- **Input Validation**: Pydantic models for all API endpoints.
- **CORS**: Configurable origins via `values.yaml`.

## 5. Remaining Risks
- **FAISS Unencrypted**: Index files on disk are not encrypted at rest. Use encrypted EBS/Persistent Volumes to mitigate.
- **Gemini over Public Internet**: Gemini API calls go over public HTTPS. Consider Private Service Connect if using Google Cloud.
