# MEDCR AI Platform - Containerization

This guide provides instructions on how to run the Legal AI Platform using Docker and Docker Compose.

## Container Architecture

- **Backend**: Python 3.12 (FastAPI) running as a non-root user.
- **Redis**: For distributed conversation memory, rate limiting, and caching.
- **Volumes**: Persistent storage for uploads, vector indexes, and logs.
- **Network**: Isolated internal network for inter-service communication.

## Quick Start

### 1. Environment Setup

Create `.env.development`, `.env.testing`, or `.env.production` in the root directory.

Example `.env.development`:
```env
GEMINI_API_KEY=your_key_here
JWT_SECRET_KEY=dev_secret
```

### 2. Development Mode

Runs with hot-reload and local filesystem mounting for the app code.

```bash
docker-compose -f docker-compose.dev.yml up --build
```

### 3. Production Mode

Optimized for deployment.

```bash
docker-compose up --build -d
```

### 4. Running Tests

Executes the test suite in an isolated container environment.

```bash
docker-compose -f docker-compose.test.yml up --build --exit-code-from backend-test
```

## Volumes & Persistence

- `backend-uploads`: Stored in `/app/uploads/documents` in the container.
- `backend-faiss`: Stored in `/app/data/faiss`.
- `backend-metadata`: Stored in `/app/data/metadata`.
- `redis-data`: Redis persistence stored in `/data`.

## Health Checks

The backend provides a `/health/ready` endpoint which is used by Docker to determine container health. You can check status with:

```bash
docker ps
```

## Troubleshooting

- **Redis Connectivity**: The backend uses the hostname `redis` to connect. Ensure both are on the same network.
- **Permissions**: The container runs as user `legalai`. If you use bind mounts, ensure the host directories have appropriate permissions.
