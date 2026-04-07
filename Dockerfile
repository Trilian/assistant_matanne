# ═══════════════════════════════════════════════════════════
# Dockerfile — Backend FastAPI pour Railway
# ═══════════════════════════════════════════════════════════
# Build:  docker build -t assistant-matanne-api .
# Run:    docker run -p 8000:8000 --env-file .env.local assistant-matanne-api

FROM python:3.13-slim AS base

# Empêcher la création de fichiers .pyc et forcer stdout non-bufferisé
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances système nécessaires (psycopg2-binary, lxml, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq-dev \
        libxml2-dev \
        libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# ─── Installation des dépendances Python ───
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── Copie du code source ───
COPY src/ src/
COPY data/ data/
COPY sql/ sql/

# ─── Utilisateur non-root (sécurité) ───
RUN mkdir -p /app/.cache && \
    adduser --disabled-password --no-create-home appuser && \
    chown -R appuser:appuser /app/.cache
USER appuser

# ─── Port exposé ───
EXPOSE 8000

# ─── Health check ───
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:' + __import__('os').environ.get('PORT', '8000') + '/health')"

# ─── Lancement uvicorn (1 worker pour Railway free tier 512MB) ───
# Railway injecte $PORT — on l'utilise avec fallback 8000
CMD uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --log-level info
