# ── Build stage ────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install runtime deps first (changes rarely → layer cached)
COPY requirements.txt requirements-ml.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-ml.txt

# ── Runtime stage ──────────────────────────────────────────────
FROM python:3.12-slim

# Non-root user
RUN groupadd --gid 1000 rag && \
    useradd --uid 1000 --gid rag --create-home rag

WORKDIR /srv/rag

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/

# Own everything by the non-root user
RUN chown -R rag:rag /srv/rag

USER rag

EXPOSE 8000

# API entrypoint — override with the worker command in docker-compose
CMD ["uvicorn", "--factory", "app.server:create_app", "--host", "0.0.0.0", "--port", "8000"]