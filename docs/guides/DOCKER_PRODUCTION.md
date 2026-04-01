# Guide Docker Production — Assistant Matanne

> **Plateforme cible** : Railway (backend FastAPI)  
> **Frontend** : Vercel (Next.js — pas de Docker)  
> **Fichiers** : `Dockerfile`, `docker-compose.staging.yml`, `frontend/Dockerfile.staging`

---

## Architecture

```
Production :
  Railway          → Backend FastAPI (Docker)        → Port 8000
  Vercel           → Frontend Next.js (buildpack)    → Port 443
  Supabase         → PostgreSQL + Auth               → Port 5432

Staging local :
  docker-compose.staging.yml  → backend + db + frontend
```

---

## Dockerfile backend — Structure

```dockerfile
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances système (psycopg2-binary, lxml, libxslt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code source (minimal — pas de tests, pas de docs)
COPY src/ src/
COPY data/ data/
COPY sql/ sql/

# Utilisateur non-root (sécurité OWASP)
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

# Vérifier le health check
curl http://localhost:8000/health

# Voir les logs
docker logs $(docker ps -q -f "ancestor=assistant-matanne-api")
```

---

## Environnement Staging complet

```bash
# Démarrer tous les services (backend + db + frontend)
python manage.py staging start
# ou directement :
docker compose -f docker-compose.staging.yml up -d --build

# Vérifier que tout tourne
docker compose -f docker-compose.staging.yml ps

# Voir les logs en temps réel
python manage.py staging logs
# ou :
docker compose -f docker-compose.staging.yml logs -f

# Arrêter
python manage.py staging stop

# Réinitialiser (DESTRUCTIF — vide la DB)
python manage.py staging reset
```

### Services du staging

| Service | Port externe | Port interne |
| --------- | ------------- | ------------- |
| `backend` (FastAPI) | 8001 | 8000 |
| `db` (PostgreSQL 16) | 5433 | 5432 |
| `frontend` (Next.js) | 3001 | 3000 |

---

## Déploiement Railway

### Prérequis

1. Compte Railway + CLI installée : `npm install -g @railway/cli`
2. Variables d'environnement configurées dans le dashboard Railway

### Variables d'environnement Railway (production)

```bash
DATABASE_URL=postgresql://user:pass@host.supabase.co:5432/db
ENVIRONMENT=production
SECRET_KEY=<clé-secrète-forte-256-bits>
MISTRAL_API_KEY=<clé-mistral>
CORS_ORIGINS=https://matanne.vercel.app
VAPID_PUBLIC_KEY=<vapid-pub>
VAPID_PRIVATE_KEY=<vapid-priv>
VAPID_ADMIN_EMAIL=admin@matanne.fr
NEXT_PUBLIC_API_URL=https://api.matanne.railway.app
```

### Déploiement

```bash
# Première fois
railway login
railway link  # associe le dépôt au projet Railway

# Déployer
railway up

# Voir les logs de déploiement
railway logs

# Ouvrir l'app
railway open
```

### Configuration Railway recommandée

| Paramètre | Valeur | Raison |
| ----------- | -------- | -------- |
| Instance type | Starter (512MB) ou Production (2GB) | 512MB = 1 worker uvicorn |
| Health check path | `/health` | Endpoint FastAPI intégré |
| Auto-deploy | Activé sur branche `main` | CI/CD automatique |
| Restart policy | ON_FAILURE | Résilience crash |

---

## Performance tuning

### Nombre de workers uvicorn

```dockerfile
# Free tier Railway (512 MB RAM) → 1 worker
CMD ["uvicorn", "src.api.main:app", "--workers", "1", ...]

# Production Railway (2 GB RAM) → formule : (2 × nb_cpu) + 1
# Sur Railway avec 2 vCPU : 5 workers
CMD ["uvicorn", "src.api.main:app", "--workers", "5", "--worker-class", "uvicorn.workers.UvicornWorker", ...]
```

### Optimiser l'image Docker

```dockerfile
# Multi-stage build pour réduire la taille de l'image finale
FROM python:3.13-slim AS builder
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.13-slim AS final
COPY --from=builder /root/.local /root/.local
# ... reste du code
```

### Cache Docker build sur Railway

Railway utilise les layer caches Docker. Placer `requirements.txt` avant `COPY src/` garantit
que les dépendances ne sont réinstallées que si `requirements.txt` change.

---

## Monitoring production

### Health checks

| Endpoint | Description |
| ---------- | ------------- |
| `GET /health` | Statut global (DB, API, cache) |
| `GET /health/db` | Connexion PostgreSQL |
| `GET /metrics` | Métriques Prometheus |

### Logs Railway

```bash
# Voir les derniers logs
railway logs --tail

# Filtrer par niveau
railway logs | grep "ERROR"
```

---

## Sécurité Docker

| Mesure | Implémentation |
| -------- | --------------- |
| Utilisateur non-root | `adduser appuser` + `USER appuser` |
| Pas de secrets dans l'image | Toujours passer via `--env-file` ou variables Railway |
| Image slim | `python:3.13-slim` (pas `python:3.13`) |
| Pas de SSH exposé | Aucun port SSH |
| Scan vulnérabilités | `docker scout cves assistant-matanne-api` |

---

## Voir aussi

- [DEPLOYMENT.md](../DEPLOYMENT.md) — Guide déploiement complet
- [DEVELOPER_SETUP.md](../DEVELOPER_SETUP.md) — Setup développeur local
- [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md) — Workflow SQL-first
