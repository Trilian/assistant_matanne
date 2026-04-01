# ðŸ  Assistant MaTanne

> Hub de gestion familiale intelligent propulsÃ© par l'IA

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16.2-black.svg)](https://nextjs.org)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green.svg)](https://supabase.com)

---

## ðŸš€ DÃ©marrage rapide

### PrÃ©requis

- Python 3.13+
- Node.js 20+
- Compte [Supabase](https://supabase.com) (PostgreSQL)
- ClÃ© API [Mistral AI](https://console.mistral.ai) (optionnel, pour les suggestions IA)

### Installation

```bash
# Backend
git clone <repo>
cd assistant_matanne
pip install -r requirements.txt
cp .env.example .env.local          # Configurer les variables

# Frontend
cd frontend
npm install
```

### Lancer l'application

```bash
# Terminal 1 â€” Backend FastAPI
python manage.py run                 # http://localhost:8000

# Terminal 2 â€” Frontend Next.js
cd frontend && npm run dev           # http://localhost:3000
```

---

## ðŸ“‹ Modules

| Module | Description | Pages |
| --- | --- | --- |
| ðŸ½ï¸ **Cuisine** | Recettes, planning repas, courses, inventaire, batch cooking, anti-gaspi | 7 |
| ðŸ‘¨â€ðŸ‘©â€ðŸ‘¦ **Famille** | Suivi Jules, activitÃ©s, routines, budget, weekend, album, anniversaires, contacts, documents, journal | 11 |
| ðŸ¡ **Maison** | Projets, jardin, entretien, charges, dÃ©penses, Ã©nergie, stocks, contrats | 9 |
| ðŸ“… **Planning** | Calendrier semaine, timeline | 2 |
| ðŸŽ® **Jeux** | Paris sportifs, loto, euromillions | 4 |
| ðŸ› ï¸ **Outils** | Chat IA, notes, mÃ©tÃ©o, minuteur, convertisseur | 6 |
| âš™ï¸ **ParamÃ¨tres** | Configuration multi-onglets | 1 |

> **~50 pages** au total, toutes connectÃ©es Ã  l'API backend.

---

## ðŸ—ï¸ Architecture

```
assistant_matanne/
â”œâ”€â”€ frontend/                  # Next.js 16 â€” SPA React/TypeScript
â”‚   â”œâ”€â”€ src/app/(app)/         #   Routes par module (~50 pages)
â”‚   â”œâ”€â”€ src/components/ui/     #   Composants shadcn/ui (21+)
â”‚   â”œâ”€â”€ src/composants/        #   Layout (sidebar, header, nav)
â”‚   â”œâ”€â”€ src/bibliotheque/api/  #   Clients API par domaine
â”‚   â”œâ”€â”€ src/crochets/          #   Custom hooks React
â”‚   â”œâ”€â”€ src/magasins/          #   Zustand stores
â”‚   â”œâ”€â”€ src/types/             #   Interfaces TypeScript
â”‚   â””â”€â”€ src/fournisseurs/      #   Providers (auth, query, theme)
â”‚
â”œâ”€â”€ src/                       # Backend Python â€” FastAPI
â”‚   â”œâ”€â”€ api/                   #   API REST (20 routers, schemas, middleware)
â”‚   â”œâ”€â”€ core/                  #   Noyau (config, DB, models, AI, cache)
â”‚   â””â”€â”€ services/              #   Logique mÃ©tier (80+ services)
â”‚
â”œâ”€â”€ sql/INIT_COMPLET.sql       # SchÃ©ma DB complet (~130 tables)
â”œâ”€â”€ tests/                     # Tests Python (pytest, 82+ fichiers)
â”œâ”€â”€ data/                      # DonnÃ©es statiques (JSON, CSV)
â””â”€â”€ docs/                      # Documentation technique
```

### Stack technique

| Couche | Technologies |
| --- | --- |
| **Backend** | FastAPI, SQLAlchemy 2.0 ORM, Pydantic v2, Mistral AI |
| **Frontend** | Next.js 16.2, TypeScript 5, Tailwind CSS v4, shadcn/ui |
| **Data Fetching** | TanStack Query v5, Axios |
| **State** | Zustand 5, react-hook-form, Zod v4 |
| **Base de donnÃ©es** | Supabase PostgreSQL (~130 tables, RLS activÃ©) |
| **Auth** | JWT Bearer (Supabase Auth + tokens API) |
| **IA** | Mistral AI (suggestions recettes, analyse paris, aide famille) |

---

## âš™ï¸ Configuration

### Variables d'environnement (.env.local)

```env
# Base de donnÃ©es Supabase
DATABASE_URL=postgresql://user:password@host:5432/db

# IA Mistral
MISTRAL_API_KEY=your_key_here

# Environnement (development | production)
ENVIRONMENT=development

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optionnel
REDIS_URL=redis://localhost:6379
VAPID_PRIVATE_KEY=your_vapid_key
CORS_ORIGINS=http://localhost:3000
FOOTBALL_DATA_API_KEY=your_football_api_key
```

> En mode `development`, l'authentification est automatique (auto-auth).

---

## ðŸ—„ï¸ Base de donnÃ©es

Le schÃ©ma complet est dans un unique fichier `sql/INIT_COMPLET.sql` (v3.0, ~130 tables).

```bash
# Initialisation : exÃ©cuter sql/INIT_COMPLET.sql dans Supabase SQL Editor ou psql
# Inclut : tables, RLS, triggers, vues, donnÃ©es de rÃ©fÃ©rence
```

---

## ðŸ§ª Tests

```bash
# Backend â€” tous les tests avec couverture
python manage.py test_coverage
# â†’ pytest --cov=src --cov-report=html --cov-report=term

# Backend â€” tests spÃ©cifiques
pytest tests/api/test_routes_recettes.py -v

# Frontend â€” Vitest (33 fichiers, 157+ tests)
cd frontend && npm test

# Frontend â€” E2E Playwright
cd frontend && npx playwright test

# Backend â€” contract tests OpenAPI (Schemathesis)
pytest tests/contracts -m contract -v

# Frontend â€” visual regression snapshots
cd frontend && npm run test:visual
```

---

## ðŸ“ Commandes utiles

```bash
python manage.py run                  # Lancer le backend (port 8000)
cd frontend && npm run dev            # Lancer le frontend (port 3000)

python manage.py format_code          # Formater (black)
python manage.py lint                 # Linter (ruff)
cd frontend && npm run lint           # Linter frontend (ESLint)
cd frontend && npx next build         # Build de vÃ©rification

python manage.py generate_requirements  # Sync requirements.txt
```

---

## ðŸ”— API

Documentation interactive aprÃ¨s dÃ©marrage du backend :

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **Health check** : http://localhost:8000/

**20 routeurs** organisÃ©s par domaine : auth, recettes, courses, inventaire, planning, suggestions IA, famille, maison, jeux, dashboard, batch-cooking, anti-gaspillage, prÃ©fÃ©rences, export, calendriers, documents, utilitaires, push, webhooks, upload.

---

## ï¿½ DÃ©ploiement

L'application est dÃ©ployÃ©e sur **3 services** :

| Service | Plateforme | URL |
| --- | --- | --- |
| Backend API | [Railway](https://railway.app) (Docker) | `https://assistant-matanne-api.up.railway.app` |
| Frontend | [Vercel](https://vercel.com) (Next.js) | `https://assistant-matanne.vercel.app` |
| Base de donnÃ©es | [Supabase](https://supabase.com) (PostgreSQL) | Dashboard Supabase |

### 1. Supabase (Base de donnÃ©es)

1. CrÃ©er un projet sur [supabase.com](https://supabase.com)
2. ExÃ©cuter `sql/INIT_COMPLET.sql` dans le **SQL Editor** (schÃ©ma complet ~130 tables, RLS, triggers)
3. RÃ©cupÃ©rer depuis **Settings > Database** :
   - `DATABASE_URL` (Connection string â†’ URI)
   - `SUPABASE_JWT_SECRET` (Settings > API > JWT Secret)
   - `NEXT_PUBLIC_SUPABASE_URL` (Settings > API > URL)
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` (Settings > API > anon key)

### 2. Railway (Backend API)

1. Connecter le repo GitHub sur [railway.app](https://railway.app)
2. Railway dÃ©tecte automatiquement le `Dockerfile` Ã  la racine
3. Configurer les **variables d'environnement** dans Railway :

| Variable | Requis | Description |
| --- | --- | --- |
| `DATABASE_URL` | âœ… | URI PostgreSQL Supabase |
| `MISTRAL_API_KEY` | âœ… | ClÃ© API Mistral AI |
| `API_SECRET_KEY` | âœ… | Secret pour tokens JWT API (`openssl rand -hex 32`) |
| `SUPABASE_JWT_SECRET` | âœ… | JWT Secret de Supabase |
| `CORS_ORIGINS` | âœ… | URL frontend Vercel (ex: `https://assistant-matanne.vercel.app`) |
| `ENVIRONMENT` | âœ… | `production` |
| `PORT` | â¬œ | Railway le fournit automatiquement (dÃ©faut: 8000) |
| `REDIS_URL` | â¬œ | Optionnel â€” cache Redis |
| `SENTRY_DSN` | â¬œ | Optionnel â€” monitoring erreurs |

4. Railway dÃ©ploie automatiquement Ã  chaque push sur `main`
5. Health check : `GET /health`
6. **AprÃ¨s le premier dÃ©ploiement**, appliquer les migrations SQL :
   ```bash
   # Via Railway CLI ou shell
   python manage.py migrate
   # Ou exÃ©cuter sql/INIT_COMPLET.sql directement dans Supabase SQL Editor
   ```

### 3. Vercel (Frontend)

1. Importer le repo sur [vercel.com](https://vercel.com), **Root Directory** = `frontend`
2. **Region** : `cdg1` (Paris) â€” configurÃ© dans `vercel.json`
3. Variables d'environnement Vercel :

| Variable | Description |
| --- | --- |
| `NEXT_PUBLIC_API_URL` | URL Railway (ex: `https://assistant-matanne-api.up.railway.app`) |
| `NEXT_PUBLIC_SUPABASE_URL` | URL Supabase (ex: `https://xxx.supabase.co`) |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ClÃ© anon Supabase |

4. Vercel dÃ©ploie automatiquement Ã  chaque push sur `main`

### CI/CD

Les workflows GitHub Actions (`.github/workflows/`) s'exÃ©cutent sur chaque push/PR :

- **deploy.yml** : Lint (ruff) + tests (pytest) + build frontend â€” gate avant dÃ©ploiement
- **tests.yml** : Tests complets (unit, integration, type-check, encoding, sÃ©curitÃ©)
- **dependabot.yml** : Mises Ã  jour automatiques des dÃ©pendances (hebdomadaire)

### VÃ©rification post-dÃ©ploiement

```bash
# Backend health
curl https://assistant-matanne-api.up.railway.app/health

# API docs
# https://assistant-matanne-api.up.railway.app/docs

# Frontend
# https://assistant-matanne.vercel.app
```

---

## ï¿½ðŸ“š Documentation

### Vue d'ensemble du projet

| Document | Description |
| --- | --- |
| [STATUS_PHASES.md](STATUS_PHASES.md) | **Ã‰tat des 28 phases (A-AC)** â€” Audit complet de l'implÃ©mentation par module |
| [ROADMAP.md](ROADMAP.md) | **Feuille de route** â€” PrioritÃ©s court/moyen/long terme + mapping phases |

### Documentation technique

| Document | Description |
| --- | --- |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architecture technique dÃ©taillÃ©e |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | RÃ©fÃ©rence complÃ¨te de l'API REST |
| [SERVICES_REFERENCE.md](docs/SERVICES_REFERENCE.md) | Documentation des services backend |
| [MODULES.md](docs/MODULES.md) | FonctionnalitÃ©s dÃ©taillÃ©es par module |
| [ERD_SCHEMA.md](docs/ERD_SCHEMA.md) | SchÃ©ma entitÃ©-relation de la DB |
| [SQLALCHEMY_SESSION_GUIDE.md](docs/SQLALCHEMY_SESSION_GUIDE.md) | Guide sessions DB |
| [UI_COMPONENTS.md](docs/UI_COMPONENTS.md) | Composants UI Next.js / shadcn |
| [PATTERNS.md](docs/PATTERNS.md) | Patterns de code rÃ©currents |
| [frontend/README.md](frontend/README.md) | Documentation frontend Next.js |

---

## ðŸ“„ Licence

Projet privÃ© â€” Usage familial uniquement.
