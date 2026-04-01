# ðŸš€ Guide de DÃ©ploiement â€” MaTanne

> **DerniÃ¨re mise Ã  jour** : Mars 2026

## Table des matiÃ¨res

1. [PrÃ©requis](#prÃ©requis)
2. [Variables d'environnement](#variables-denvironnement)
3. [DÃ©ploiement Local (DÃ©veloppement)](#dÃ©ploiement-local)
4. [DÃ©ploiement Docker (Backend)](#dÃ©ploiement-docker)
5. [DÃ©ploiement Frontend â€” Vercel](#dÃ©ploiement-frontend--vercel)
6. [Base de donnÃ©es â€” Supabase](#base-de-donnÃ©es--supabase)
7. [DÃ©ploiement Backend â€” Railway](#dÃ©ploiement-backend--railway)
8. [VÃ©rification post-dÃ©ploiement](#vÃ©rification-post-dÃ©ploiement)

---

## PrÃ©requis

| Composant        | Version minimale | RÃ´le                         |
| ----------------- | ----------------- | ------------------------------ |
| Python          | 3.13+           | Runtime backend               |
| Node.js         | 20+             | Runtime frontend              |
| Docker          | 24+             | Conteneurisation backend      |
| Compte Supabase | â€”               | PostgreSQL + Auth             |
| Compte Vercel   | â€”               | HÃ©bergement frontend Next.js  |
| Compte Railway  | â€”               | HÃ©bergement backend FastAPI   |

---

## Variables d'environnement

> **Important** : Les fichiers `.env*` ne servent qu'au **dÃ©veloppement local**.
> En production, les variables sont configurÃ©es dans les dashboards **Vercel** (frontend) et **Railway** (backend).

### Fichier unique : `.env.local` (Ã  la racine)

Le projet utilise un **seul fichier** `.env.local` Ã  la racine pour toutes les variables (backend + frontend).
Next.js n'expose cÃ´tÃ© navigateur que les variables prÃ©fixÃ©es `NEXT_PUBLIC_` â€” le reste est ignorÃ© par le frontend.

```env
# â”€â”€â”€ BACKEND â”€â”€â”€
DATABASE_URL=postgresql://user:password@host:5432/database
SUPABASE_URL=https://xxxxxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJxxxxxxxxxxxxxxxxxxxxx
SUPABASE_SERVICE_ROLE_KEY=eyJxxxxxxxxxxxxxxxxxxxxx
JWT_SECRET_KEY=votre_secret_jwt_tres_long_et_aleatoire
MISTRAL_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000

# â”€â”€â”€ FRONTEND (NEXT_PUBLIC_*) â”€â”€â”€
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxxxxxxxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxxxxxxxxxxxxxxxxxxxx
NEXT_PUBLIC_VAPID_PUBLIC_KEY=
```

Copier le template : `cp .env.example .env.local` puis remplir avec vos valeurs.

> âš ï¸ Ne jamais committer `.env.local`. Il est dans `.gitignore`.

### Variables Vercel (production frontend)

Dans le dashboard Vercel â†’ Settings â†’ Environment Variables :

| Variable | Exemple | Description |
| ---------- | --------- | ------------- |
| `NEXT_PUBLIC_API_URL` | `https://votre-backend.railway.app` | URL du backend Railway |
| `NEXT_PUBLIC_WS_URL` | `wss://votre-backend.railway.app` | WebSocket backend |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://xxxx.supabase.co` | Instance Supabase |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJxxx...` | ClÃ© anon Supabase |
| `NEXT_PUBLIC_VAPID_PUBLIC_KEY` | `BIxxx...` | Push notifications |

### Variables Railway (production backend)

Dans le dashboard Railway â†’ Variables :

| Variable | Description |
| ---------- | ------------- |
| `DATABASE_URL` | URL PostgreSQL Supabase |
| `SUPABASE_URL` | Instance Supabase |
| `SUPABASE_ANON_KEY` | ClÃ© anon |
| `SUPABASE_SERVICE_ROLE_KEY` | ClÃ© service role |
| `JWT_SECRET_KEY` | Secret pour tokens JWT |
| `MISTRAL_API_KEY` | ClÃ© API Mistral |
| `ENVIRONMENT` | `production` |
| `CORS_ORIGINS` | `https://votre-frontend.vercel.app` |

---

## DÃ©ploiement Local

### Backend

```bash
# 1. Cloner le dÃ©pÃ´t
git clone https://github.com/vous/assistant_matanne.git
cd assistant_matanne

# 2. CrÃ©er et activer l'environnement virtuel
python -m venv .venv
.\.venv\Scripts\activate   # Windows
source .venv/bin/activate  # Linux/macOS

# 3. Installer les dÃ©pendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env.local
# Ã‰diter .env.local avec vos valeurs

# 5. Initialiser la base de donnÃ©es (voir section Supabase)

# 6. Lancer le serveur de dÃ©veloppement
python manage.py run
# â†’ http://localhost:8000
# â†’ http://localhost:8000/docs (Swagger UI)
```

### Frontend

```bash
cd frontend

# 1. Installer les dÃ©pendances
npm install

# 2. Lancer le serveur de dÃ©veloppement
# (lit automatiquement ../.env.local via --env-file dans package.json)
npm run dev
# â†’ http://localhost:3000
```

---

## DÃ©ploiement Docker

Le backend est conteneurisÃ© avec le `Dockerfile` Ã  la racine.

### Build et run local

```bash
# Build
docker build -t assistant-matanne-api .

# Run avec le fichier .env.local
docker run -p 8000:8000 --env-file .env.local assistant-matanne-api

# Run en dÃ©tachÃ©
docker run -d -p 8000:8000 --env-file .env.local --name matanne-api assistant-matanne-api
```

### Docker Compose (dÃ©veloppement local complet)

```yaml
# docker-compose.yml (Ã  crÃ©er si nÃ©cessaire)
version: '3.9'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env.local
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Variables d'environnement Docker

Toutes les variables dans `.env.local` sont passÃ©es avec `--env-file`. En production, utiliser les secrets de la plateforme (Railway secrets, Vercel env vars).

---

## DÃ©ploiement Frontend â€” Vercel

### MÃ©thode GitHub (recommandÃ©e)

1. **Connecter le dÃ©pÃ´t** : Vercel â†’ "Import Project" â†’ GitHub â†’ `assistant_matanne`

2. **Configuration build** :
   - **Root Directory** : `frontend`
   - **Build Command** : `npm run build`
   - **Output Directory** : `.next`
   - **Framework Preset** : Next.js

3. **Variables d'environnement** (dans Settings â†’ Environment Variables) :
   ```
   NEXT_PUBLIC_API_URL = https://votre-backend.railway.app
   NEXT_PUBLIC_WS_URL = wss://votre-backend.railway.app
   NEXT_PUBLIC_SUPABASE_URL = https://xxxxxx.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY = eyJxxx...
   NEXT_PUBLIC_VAPID_PUBLIC_KEY = BIxxx...
   ```
   > Les fichiers `.env*` du repo ne sont **PAS** utilisÃ©s par Vercel. Seules les variables du dashboard comptent.

4. **DÃ©ploiement** : automatique sur chaque push `main`

### MÃ©thode CLI

```bash
cd frontend
npx vercel --prod
```

### VÃ©rifier le build avant dÃ©ploiement

```bash
cd frontend
npm run build   # VÃ©rifie les erreurs TypeScript et de build
npm run lint    # VÃ©rifie le linting ESLint
```

---

## Base de donnÃ©es â€” Supabase

### Initialisation du schÃ©ma (premiÃ¨re fois)

1. **CrÃ©er un projet Supabase** : https://supabase.com/dashboard

2. **RÃ©cupÃ©rer les credentials** dans Settings â†’ API :
   - Project URL â†’ `SUPABASE_URL`
   - `anon` key â†’ `SUPABASE_ANON_KEY`
   - `service_role` key â†’ `SUPABASE_SERVICE_ROLE_KEY`
   - Database URL â†’ `DATABASE_URL` (Settings â†’ Database)

3. **ExÃ©cuter le schÃ©ma initial** dans Supabase SQL Editor :
   ```sql
   -- Copier et coller le contenu de sql/INIT_COMPLET.sql
   -- Ce fichier crÃ©e toutes les tables, RLS, triggers et vues
   ```

4. **VÃ©rifier la connexion** :
   ```bash
   python -c "from src.core.db import obtenir_moteur; obtenir_moteur().connect(); print('OK')"
   ```

### Appliquer des migrations

```bash
# CrÃ©er une nouvelle migration
python manage.py create-migration

# Lister les migrations en attente
python manage.py migrate --dry-run

# Appliquer les migrations
python manage.py migrate
```

Les fichiers de migration sont dans `sql/migrations/`. La table `schema_migrations` en DB trace les migrations appliquÃ©es.

### Row Level Security (RLS)

Toutes les tables ont RLS activÃ©. Les politiques sont dÃ©finies dans `sql/INIT_COMPLET.sql`. Toujours utiliser le `service_role_key` dans le backend pour contourner RLS (accÃ¨s admin), et le token JWT utilisateur pour l'accÃ¨s filtrÃ©.

### Sauvegarde

```bash
# Export via pg_dump (remplacer les credentials)
pg_dump "postgresql://user:pass@host:5432/db" > backup_$(date +%Y%m%d).sql
```

---

## DÃ©ploiement Backend â€” Railway

### MÃ©thode GitHub (recommandÃ©e)

1. **CrÃ©er un projet Railway** : https://railway.app/new

2. **Connecter le dÃ©pÃ´t GitHub**

3. **Configuration du service** :
   - **Root Directory** : `/` (racine du projet)
   - **Start Command** : `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT --workers 1`
   - **Build Command** : `pip install -r requirements.txt`
   - Ou utiliser le **Dockerfile** (Railway le dÃ©tecte automatiquement)

4. **Variables d'environnement** dans Railway â†’ Variables :
   ```
   DATABASE_URL = postgresql://...
   SUPABASE_URL = https://...
   SUPABASE_ANON_KEY = eyJ...
   SUPABASE_SERVICE_ROLE_KEY = eyJ...
   JWT_SECRET_KEY = ...
   MISTRAL_API_KEY = ...
   ENVIRONMENT = production
   CORS_ORIGINS = https://votre-frontend.vercel.app
   ```

5. **Domaine** : Railway fournit un domaine automatique `*.railway.app`. L'utiliser comme `NEXT_PUBLIC_API_URL` dans Vercel.

### Scaling

Le `Dockerfile` utilise 1 worker (`--workers 1`) pour Ã©conomiser la RAM sur le plan gratuit Railway (512 MB). Augmenter selon les ressources disponibles.

---

## VÃ©rification post-dÃ©ploiement

### Backend

```bash
# Health check
curl https://votre-backend.railway.app/health
# â†’ {"status": "healthy", "version": "1.0", ...}

# Documentation Swagger
open https://votre-backend.railway.app/docs

# VÃ©rifier l'authentification
curl -X POST https://votre-backend.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test@example.com", "password": "password"}'
```

### Frontend

```bash
# VÃ©rifier la page de connexion
open https://votre-frontend.vercel.app/connexion

# VÃ©rifier les variables d'environnement chargÃ©es
open https://votre-frontend.vercel.app/api/health
```

### Checklist complÃ¨te

- [ ] Backend rÃ©pond sur `/health`
- [ ] Swagger accessible sur `/docs`
- [ ] Frontend charge le login
- [ ] Login fonctionne (token JWT reÃ§u)
- [ ] Dashboard charge aprÃ¨s login
- [ ] RequÃªtes API rÃ©ussies (network tab = 200)
- [ ] Pas d'erreur CORS dans la console browser
- [ ] RLS Supabase filtre correctement les donnÃ©es utilisateur
