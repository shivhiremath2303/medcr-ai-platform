# --- Stage 1: Build base ---
FROM python:3.12-slim as builder

# Set environment variables
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

# Install dependencies
COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install --upgrade pip && \
    pip install --user --no-warn-script-location -r requirements.txt

# Pre-download ML models to speed up container startup and ensure CI stability
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" && \
    python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

# --- Stage 2: Production ---
FROM python:3.12-slim as runtime

# Create a non-root user
RUN groupadd -r legalai && useradd -r -g legalai legalai

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    SENTENCE_TRANSFORMERS_HOME=/home/legalai/.cache/torch/sentence_transformers

# Set work directory
WORKDIR /app

# Copy dependencies and pre-downloaded models from builder
COPY --from=builder /root/.local /home/legalai/.local
COPY --from=builder /root/.cache /home/legalai/.cache

ENV PATH=/home/legalai/.local/bin:$PATH

# Install runtime system dependencies (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p uploads/documents data/faiss data/metadata data/temp data/cache logs && \
    chown -R legalai:legalai /app /home/legalai/.cache

# Switch to non-root user
USER legalai

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ready || exit 1

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
