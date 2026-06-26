# =============================================================================
# Zava AI Agent Platform — Python API
# Dockerfile — built with repo root as build context:
#   docker build -f src/python/Dockerfile -t zava-api-python .
#
# The build context must be the REPO ROOT so the data/ seed directory
# is accessible for github (local) mode.
# =============================================================================

# ---- builder stage ----
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build deps
RUN pip install --no-cache-dir hatchling

COPY src/python/pyproject.toml .
COPY src/python/app/ ./app/

# Install production deps into /install
RUN pip install --no-cache-dir --prefix=/install "."

# ---- runtime stage ----
FROM python:3.12-slim AS runtime

WORKDIR /app

# Non-root user for security
RUN groupadd -r zava && useradd -r -g zava -d /app -s /sbin/nologin zava

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY src/python/app/ ./app/

# Copy seed data for github (local) mode
COPY data/ ./data/

# Set data dir so the app can find seed files
ENV DATA_DIR=/app/data

# Default runtime env vars (override in Container Apps)
ENV INFERENCE_PROVIDER=github \
    EMBEDDINGS_PROVIDER=github \
    PORT=8000

EXPOSE 8000

USER zava

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
