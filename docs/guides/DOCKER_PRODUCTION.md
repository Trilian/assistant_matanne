# Guide Docker Production â€” Assistant Matanne

> **Plateforme cible** : Railway (backend FastAPI)  
> **Frontend** : Vercel (Next.js â€” pas de Docker)  
> **Fichiers** : `Dockerfile`, `docker-compose.staging.yml`, `frontend/Dockerfile.staging`

---

## Architecture

```
Production :
  Railway          â†’ Backend FastAPI (Docker)        â†’ Port 8000
  Vercel           â†’ Frontend Next.js (buildpack)    â†’ Port 443
  Supabase         â†’ PostgreSQL + Auth               â†’ Port 5432

Staging local :
  docker-compose.staging.yml  â†’ backend + db + frontend
```

---

## Dockerfile backend â€” Structure

```dockerfile
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# DÃ©pendances systÃ¨me (psycopg2-binary, lxml, libxslt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# DÃ©pendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code source (minimal â€” pas de tests, pas de docs)
COPY src/ src/
COPY data/ data/
COPY sql/ sql/

# Utilisateur non-root (sÃ©curitÃ© OWASP)
RUN adduser --disabled-password --no-create-home appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# 1 worker pour Railway free tier (512MB RAM)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "1", "--log-level", "info"]
```

---

## Build et test local

```bash
# Build l'image
docker build -t assistant-matanne-api .

# Tester avec les variables d'environnement
docker run -p 8000:8000 --env-file .env.local assistant-matanne-api

# VÃ©rifier le health check
curl http://localhost:8000/health

# Voir les logs
docker logs $(docker ps -q -f "ancestor=assistant-matanne-api")
```

---

## Environnement Staging complet

```bash
# DÃ©marrer tous les services (backend + db + frontend)
python manage.py staging start
# ou directement :
docker compose -f docker-compose.staging.yml up -d --build

# VÃ©rifier que tout tourne
docker compose -f docker-compose.staging.yml ps

# Voir les logs en temps rÃ©el
python manage.py staging logs
# ou :
docker compose -f docker-compose.staging.yml logs -f

# ArrÃªter
python manage.py staging stop

# RÃ©initialiser (DESTRUCTIF â€” vide la DB)
python manage.py staging reset
```

### Services du staging

| Service | Port externe | Port interne |
| --------- | ------------- | ------------- |
| `backend` (FastAPI) | 8001 | 8000 |
| `db` (PostgreSQL 16) | 5433 | 5432 |
| `frontend` (Next.js) | 3001 | 3000 |

---

## DÃ©ploiement Railway

### PrÃ©requis

1. Compte Railway + CLI installÃ©e : `npm install -g @railway/cli`
2. Variables d'environnement configurÃ©es dans le dashboard Railway

### Variables d'environnement Railway (production)

```bash
DATABASE_URL=postgresql://user:pass@host.supabase.co:5432/db
ENVIRONMENT=production
SECRET_KEY=<clÃ©-secrÃ¨te-forte-256-bits>
MISTRAL_API_KEY=<clÃ©-mistral>
CORS_ORIGINS=https://matanne.vercel.app
VAPID_PUBLIC_KEY=<vapid-pub>
VAPID_PRIVATE_KEY=<vapid-priv>
VAPID_ADMIN_EMAIL=admin@matanne.fr
NEXT_PUBLIC_API_URL=https://api.matanne.railway.app
```

### DÃ©ploiement

```bash
# PremiÃ¨re fois
railway login
railway link  # associe le dÃ©pÃ´t au projet Railway

# DÃ©ployer
railway up

# Voir les logs de dÃ©ploiement
railway logs

# Ouvrir l'app
railway open
```

### Configuration Railway recommandÃ©e

| ParamÃ¨tre | Valeur | Raison |
| ----------- | -------- | -------- |
| Instance type | Starter (512MB) ou Production (2GB) | 512MB = 1 worker uvicorn |
| Health check path | `/health` | Endpoint FastAPI intÃ©grÃ© |
| Auto-deploy | ActivÃ© sur branche `main` | CI/CD automatique |
| Restart policy | ON_FAILURE | RÃ©silience crash |

---

## Performance tuning

### Nombre de workers uvicorn

```dockerfile
# Free tier Railway (512 MB RAM) â†’ 1 worker
CMD ["uvicorn", "src.api.main:app", "--workers", "1", ...]

# Production Railway (2 GB RAM) â†’ formule : (2 Ã— nb_cpu) + 1
# Sur Railway avec 2 vCPU : 5 workers
CMD ["uvicorn", "src.api.main:app", "--workers", "5", "--worker-class", "uvicorn.workers.UvicornWorker", ...]
```

### Optimiser l'image Docker

```dockerfile
# Multi-stage build pour rÃ©duire la taille de l'image finale
FROM python:3.13-slim AS builder
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.13-slim AS final
COPY --from=builder /root/.local /root/.local
# ... reste du code
```

### Cache Docker build sur Railway

Railway utilise les layer caches Docker. Placer `requirements.txt` avant `COPY src/` garantit
que les dÃ©pendances ne sont rÃ©installÃ©es que si `requirements.txt` change.

---

## Monitoring production

### Health checks

| Endpoint | Description |
| ---------- | ------------- |
| `GET /health` | Statut global (DB, API, cache) |
| `GET /health/db` | Connexion PostgreSQL |
| `GET /metrics` | MÃ©triques Prometheus |

### Logs Railway

```bash
# Voir les derniers logs
railway logs --tail

# Filtrer par niveau
railway logs | grep "ERROR"
```

---

## SÃ©curitÃ© Docker

| Mesure | ImplÃ©mentation |
| -------- | --------------- |
| Utilisateur non-root | `adduser appuser` + `USER appuser` |
| Pas de secrets dans l'image | Toujours passer via `--env-file` ou variables Railway |
| Image slim | `python:3.13-slim` (pas `python:3.13`) |
| Pas de SSH exposÃ© | Aucun port SSH |
| Scan vulnÃ©rabilitÃ©s | `docker scout cves assistant-matanne-api` |

---

## Voir aussi

- [DEPLOYMENT.md](../DEPLOYMENT.md) â€” Guide dÃ©ploiement complet
- [DEVELOPER_SETUP.md](../DEVELOPER_SETUP.md) â€” Setup dÃ©veloppeur local
- [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md) â€” Workflow SQL-first
