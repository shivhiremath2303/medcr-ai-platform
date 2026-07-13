# --- Stage 1: Build base ---
FROM python:3.12-slim-bookworm as builder

# Set environment variables for build safety
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /build

# Install dependencies into a specific directory for easy transfer
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-warn-script-location -r requirements.txt

# Pre-download ML models to builder cache
# We use a temp home to ensure the builder's environment doesn't leak into the install prefix
ENV SENTENCE_TRANSFORMERS_HOME=/install/cache/torch/sentence_transformers
RUN mkdir -p $SENTENCE_TRANSFORMERS_HOME && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', cache_folder='$SENTENCE_TRANSFORMERS_HOME')" && \
    python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', cache_folder='$SENTENCE_TRANSFORMERS_HOME')"

# --- Stage 2: Production Hardening ---
FROM python:3.12-slim-bookworm as runtime

# 1. Define explicit security identity (UID/GID 10001 is common for non-privileged services)
ARG USER_ID=10001
ARG GROUP_ID=10001

RUN groupadd -g ${GROUP_ID} legalai && \
    useradd -l -u ${USER_ID} -g legalai -m -s /sbin/nologin legalai

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/home/legalai/.local/bin:$PATH" \
    SENTENCE_TRANSFORMERS_HOME=/app/data/cache/models

# 3. Secure Workspace Preparation
WORKDIR /app

# 4. Copy dependencies from builder
COPY --from=builder /install/lib /usr/local/lib
COPY --from=builder /install/bin /usr/local/bin
COPY --from=builder /install/cache/torch/sentence_transformers /app/data/cache/models

# 5. Copy Application Source
# We copy this as root first to ensure immutability
COPY app /app/app
COPY main.py /app/

# 6. Create structure for writable directories (to be used as volumes or tmpfs)
# We place these under /app but they must be owned by the app user
RUN mkdir -p /app/uploads/documents /app/data/faiss /app/data/metadata /app/data/temp /app/data/cache /app/logs && \
    chown -R legalai:legalai /app/uploads /app/data /app/logs

# 7. Harden permissions
# - Source code (/app/app) should be owned by root and read-only for legalai
# - This prevents "In-container code modification" if the process is compromised
RUN chown -R root:root /app && \
    chown -R legalai:legalai /app/uploads /app/data /app/logs && \
    chmod -R 555 /app/app && \
    chmod 555 /app/main.py

# 8. Install runtime essentials only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Switch to non-root user
USER legalai

# Expose port
EXPOSE 8000

# 9. Hardened Healthcheck
# Uses a non-shell form for efficiency and security
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["curl", "-f", "http://localhost:8000/health/ready"]

# 10. Execution
# We use uvicorn directly. In high-security environments, consider a process manager like gunicorn with UvicornWorker.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning"]
