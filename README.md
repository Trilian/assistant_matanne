# 🏠 Assistant MaTanne

> Hub de gestion familiale intelligent propulsé par l'IA

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16.2-black.svg)](https://nextjs.org)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green.svg)](https://supabase.com)

---

## 🚀 Démarrage rapide

### Prérequis

- Python 3.13+
- Node.js 20+
- Compte [Supabase](https://supabase.com) (PostgreSQL)
- Clé API [Mistral AI](https://console.mistral.ai) (optionnel, pour les suggestions IA)

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
# Terminal 1 — Backend FastAPI
python manage.py run                 # http://localhost:8000

# Terminal 2 — Frontend Next.js
cd frontend && npm run dev           # http://localhost:3000
```

---

## 📋 Modules

| Module | Description | Pages |
|---|---|---|
| 🍽️ **Cuisine** | Recettes, planning repas, courses, inventaire, batch cooking, anti-gaspi | 7 |
| 👨‍👩‍👦 **Famille** | Suivi Jules, activités, routines, budget, weekend, album, anniversaires, contacts, documents, journal | 11 |
| 🏡 **Maison** | Projets, jardin, entretien, charges, dépenses, énergie, stocks, contrats | 9 |
| 📅 **Planning** | Calendrier semaine, timeline | 2 |
| 🎮 **Jeux** | Paris sportifs, loto, euromillions | 4 |
| 🛠️ **Outils** | Chat IA, notes, météo, minuteur, convertisseur | 6 |
| ⚙️ **Paramètres** | Configuration multi-onglets | 1 |

> **~50 pages** au total, toutes connectées à l'API backend.

---

## 🏗️ Architecture

```
assistant_matanne/
├── frontend/                  # Next.js 16 — SPA React/TypeScript
│   ├── src/app/(app)/         #   Routes par module (~50 pages)
│   ├── src/components/ui/     #   Composants shadcn/ui (21+)
│   ├── src/composants/        #   Layout (sidebar, header, nav)
│   ├── src/bibliotheque/api/  #   Clients API par domaine
│   ├── src/crochets/          #   Custom hooks React
│   ├── src/magasins/          #   Zustand stores
│   ├── src/types/             #   Interfaces TypeScript
│   └── src/fournisseurs/      #   Providers (auth, query, theme)
│
├── src/                       # Backend Python — FastAPI
│   ├── api/                   #   API REST (20 routers, schemas, middleware)
│   ├── core/                  #   Noyau (config, DB, models, AI, cache)
│   └── services/              #   Logique métier (80+ services)
│
├── sql/INIT_COMPLET.sql       # Schéma DB complet (~130 tables)
├── tests/                     # Tests Python (pytest, 82+ fichiers)
├── data/                      # Données statiques (JSON, CSV)
└── docs/                      # Documentation technique
```

### Stack technique

| Couche | Technologies |
|---|---|
| **Backend** | FastAPI, SQLAlchemy 2.0 ORM, Pydantic v2, Mistral AI |
| **Frontend** | Next.js 16.2, TypeScript 5, Tailwind CSS v4, shadcn/ui |
| **Data Fetching** | TanStack Query v5, Axios |
| **State** | Zustand 5, react-hook-form, Zod v4 |
| **Base de données** | Supabase PostgreSQL (~130 tables, RLS activé) |
| **Auth** | JWT Bearer (Supabase Auth + tokens API) |
| **IA** | Mistral AI (suggestions recettes, analyse paris, aide famille) |

---

## ⚙️ Configuration

### Variables d'environnement (.env.local)

```env
# Base de données Supabase
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

## 🗄️ Base de données

Le schéma complet est dans un unique fichier `sql/INIT_COMPLET.sql` (v3.0, ~130 tables).

```bash
# Initialisation : exécuter sql/INIT_COMPLET.sql dans Supabase SQL Editor ou psql
# Inclut : tables, RLS, triggers, vues, données de référence
```

---

## 🧪 Tests

```bash
# Backend — tous les tests avec couverture
python manage.py test_coverage
# → pytest --cov=src --cov-report=html --cov-report=term

# Backend — tests spécifiques
pytest tests/api/test_routes_recettes.py -v

# Frontend — Vitest (33 fichiers, 157+ tests)
cd frontend && npm test

# Frontend — E2E Playwright
cd frontend && npx playwright test
```

---

## 📝 Commandes utiles

```bash
python manage.py run                  # Lancer le backend (port 8000)
cd frontend && npm run dev            # Lancer le frontend (port 3000)

python manage.py format_code          # Formater (black)
python manage.py lint                 # Linter (ruff)
cd frontend && npm run lint           # Linter frontend (ESLint)
cd frontend && npx next build         # Build de vérification

python manage.py generate_requirements  # Sync requirements.txt
```

---

## 🔗 API

Documentation interactive après démarrage du backend :

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **Health check** : http://localhost:8000/

**20 routeurs** organisés par domaine : auth, recettes, courses, inventaire, planning, suggestions IA, famille, maison, jeux, dashboard, batch-cooking, anti-gaspillage, préférences, export, calendriers, documents, utilitaires, push, webhooks, upload.

---

## � Déploiement

L'application est déployée sur **3 services** :

| Service | Plateforme | URL |
|---|---|---|
| Backend API | [Railway](https://railway.app) (Docker) | `https://assistant-matanne-api.up.railway.app` |
| Frontend | [Vercel](https://vercel.com) (Next.js) | `https://assistant-matanne.vercel.app` |
| Base de données | [Supabase](https://supabase.com) (PostgreSQL) | Dashboard Supabase |

### 1. Supabase (Base de données)

1. Créer un projet sur [supabase.com](https://supabase.com)
2. Exécuter `sql/INIT_COMPLET.sql` dans le **SQL Editor** (schéma complet ~130 tables, RLS, triggers)
3. Récupérer depuis **Settings > Database** :
   - `DATABASE_URL` (Connection string → URI)
   - `SUPABASE_JWT_SECRET` (Settings > API > JWT Secret)
   - `NEXT_PUBLIC_SUPABASE_URL` (Settings > API > URL)
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` (Settings > API > anon key)

### 2. Railway (Backend API)

1. Connecter le repo GitHub sur [railway.app](https://railway.app)
2. Railway détecte automatiquement le `Dockerfile` à la racine
3. Configurer les **variables d'environnement** dans Railway :

| Variable | Requis | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | URI PostgreSQL Supabase |
| `MISTRAL_API_KEY` | ✅ | Clé API Mistral AI |
| `API_SECRET_KEY` | ✅ | Secret pour tokens JWT API (`openssl rand -hex 32`) |
| `SUPABASE_JWT_SECRET` | ✅ | JWT Secret de Supabase |
| `CORS_ORIGINS` | ✅ | URL frontend Vercel (ex: `https://assistant-matanne.vercel.app`) |
| `ENVIRONMENT` | ✅ | `production` |
| `PORT` | ⬜ | Railway le fournit automatiquement (défaut: 8000) |
| `REDIS_URL` | ⬜ | Optionnel — cache Redis |
| `SENTRY_DSN` | ⬜ | Optionnel — monitoring erreurs |

4. Railway déploie automatiquement à chaque push sur `main`
5. Health check : `GET /health`
6. **Après le premier déploiement**, appliquer les migrations SQL :
   ```bash
   # Via Railway CLI ou shell
   python manage.py migrate
   # Ou exécuter sql/INIT_COMPLET.sql directement dans Supabase SQL Editor
   ```

### 3. Vercel (Frontend)

1. Importer le repo sur [vercel.com](https://vercel.com), **Root Directory** = `frontend`
2. **Region** : `cdg1` (Paris) — configuré dans `vercel.json`
3. Variables d'environnement Vercel :

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | URL Railway (ex: `https://assistant-matanne-api.up.railway.app`) |
| `NEXT_PUBLIC_SUPABASE_URL` | URL Supabase (ex: `https://xxx.supabase.co`) |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Clé anon Supabase |

4. Vercel déploie automatiquement à chaque push sur `main`

### CI/CD

Les workflows GitHub Actions (`.github/workflows/`) s'exécutent sur chaque push/PR :

- **deploy.yml** : Lint (ruff) + tests (pytest) + build frontend — gate avant déploiement
- **tests.yml** : Tests complets (unit, integration, type-check, encoding, sécurité)
- **dependabot.yml** : Mises à jour automatiques des dépendances (hebdomadaire)

### Vérification post-déploiement

```bash
# Backend health
curl https://assistant-matanne-api.up.railway.app/health

# API docs
# https://assistant-matanne-api.up.railway.app/docs

# Frontend
# https://assistant-matanne.vercel.app
```

---

## �📚 Documentation

### Vue d'ensemble du projet

| Document | Description |
|---|---|
| [STATUS_PHASES.md](STATUS_PHASES.md) | **État des 28 phases (A-AC)** — Audit complet de l'implémentation par module |
| [ROADMAP.md](ROADMAP.md) | **Feuille de route** — Priorités court/moyen/long terme + mapping phases |

### Documentation technique

| Document | Description |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architecture technique détaillée |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | Référence complète de l'API REST |
| [SERVICES_REFERENCE.md](docs/SERVICES_REFERENCE.md) | Documentation des services backend |
| [MODULES.md](docs/MODULES.md) | Fonctionnalités détaillées par module |
| [ERD_SCHEMA.md](docs/ERD_SCHEMA.md) | Schéma entité-relation de la DB |
| [SQLALCHEMY_SESSION_GUIDE.md](docs/SQLALCHEMY_SESSION_GUIDE.md) | Guide sessions DB |
| [UI_COMPONENTS.md](docs/UI_COMPONENTS.md) | Composants UI Next.js / shadcn |
| [PATTERNS.md](docs/PATTERNS.md) | Patterns de code récurrents |
| [frontend/README.md](frontend/README.md) | Documentation frontend Next.js |

---

## 📄 Licence

Projet privé — Usage familial uniquement.