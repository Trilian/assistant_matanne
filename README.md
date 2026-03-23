# 🏠 Assistant Matanne

> Hub de gestion familiale intelligent propulsé par l'IA

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16.2-black.svg)](https://nextjs.org)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green.svg)](https://supabase.com)

## 🚀 Démarrage rapide

```bash
# 1. Cloner et installer le backend
git clone <repo>
cd assistant_matanne
pip install -r requirements.txt

# 2. Lancer le backend FastAPI
python manage.py run          # http://localhost:8000

# 3. Installer et lancer le frontend Next.js
cd frontend
npm install
npm run dev                   # http://localhost:3000
```

## 📋 Modules

| Module | Description | Pages |
|---|---|---|
| 🍽️ **Cuisine** | Recettes, planning repas, courses, inventaire, batch cooking, anti-gaspi | 7 |
| 👨‍👩‍👦 **Famille** | Suivi Jules, activités, routines, budget, weekend, album, anniversaires, contacts, documents, journal | 11 |
| 🏡 **Maison** | Projets, jardin, entretien, charges, dépenses, énergie, stocks, visualisation | 9 |
| 📅 **Planning** | Calendrier semaine, timeline | 2 |
| 🎮 **Jeux** | Paris sportifs, loto, euromillions | 4 |
| 🛠️ **Outils** | Chat IA, notes, météo, minuteur, convertisseur | 6 |
| ⚙️ **Paramètres** | Configuration multi-onglets | 1 |

## 🏗️ Architecture

```
assistant_matanne/
├── frontend/               # Next.js 16 (React/TypeScript)
│   ├── src/app/(app)/      # Routes par module (~52 pages)
│   ├── src/components/     # Composants shadcn/ui (21+)
│   ├── src/composants/     # Layout (sidebar, header, nav)
│   ├── src/bibliotheque/api/ # Clients API par domaine
│   ├── src/crochets/       # Custom hooks React
│   ├── src/magasins/       # Zustand stores
│   ├── src/types/          # Interfaces TypeScript
│   └── src/fournisseurs/   # Providers (auth, query, theme)
├── src/                    # Backend Python (FastAPI)
│   ├── api/                # API REST (20 routers, schemas, middleware)
│   ├── core/               # Noyau (config, DB, models, AI, cache)
│   └── services/           # Logique métier (@service_factory)
├── sql/                    # Schéma DB + migrations
├── tests/                  # Tests Python (pytest)
├── data/                   # Données statiques (JSON, CSV)
└── docs/                   # Documentation
```

### Stack technique

| Couche | Technologies |
|---|---|
| **Backend** | FastAPI, SQLAlchemy 2.0, Pydantic v2, Mistral AI |
| **Frontend** | Next.js 16.2.1, TypeScript 5, Tailwind CSS v4, shadcn/ui |
| **Data Fetching** | TanStack Query v5, Axios |
| **State** | Zustand 5, react-hook-form 7.72, Zod 4.3.6 |
| **Base de données** | Supabase PostgreSQL, migrations SQL-file |
| **Auth** | JWT Bearer (Supabase Auth + tokens API) |

## ⚙️ Configuration

### Variables d'environnement (.env.local)

```env
# Base de données Supabase
DATABASE_URL=postgresql://user:password@host:5432/db

# IA Mistral
MISTRAL_API_KEY=your_key_here

# Environnement (development|production)
ENVIRONMENT=development

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optionnel
REDIS_URL=redis://localhost:6379
VAPID_PRIVATE_KEY=your_vapid_key
CORS_ORIGINS=http://localhost:3000
```

### Fichiers de configuration

| Fichier | Usage |
|---|---|
| `.env.local` | Variables d'environnement locales (prioritaire) |
| `.env` | Variables par défaut |
| `pyproject.toml` | Dépendances Python, config tests/lint |
| `frontend/package.json` | Dépendances frontend, scripts npm |

## 🗄️ Base de données

```bash
# Initialisation complète : exécuter sql/INIT_COMPLET.sql dans Supabase SQL Editor

# Créer une migration SQL
python manage.py create-migration

# Appliquer les migrations en attente
python manage.py migrate
```

Les fichiers SQL dans `sql/migrations/` sont numérotés (`001_xxx.sql`, `002_xxx.sql`, ...) et appliqués automatiquement dans l'ordre par `GestionnaireMigrations`.

## 🧪 Tests

```bash
# Backend — tous les tests avec couverture
python manage.py test_coverage

# Backend — tests spécifiques
pytest tests/test_recettes.py -v

# Backend — un seul test
pytest tests/test_recettes.py::test_method -v

# Frontend — Vitest
cd frontend && npm test

# Frontend — E2E Playwright
cd frontend && npx playwright test
```

## 📝 Commandes utiles

```bash
# Lancer le backend FastAPI
python manage.py run

# Lancer le frontend Next.js
cd frontend && npm run dev

# Formater le code Python
python manage.py format_code

# Linter Python (ruff)
python manage.py lint

# Linter Frontend (ESLint)
cd frontend && npm run lint

# Build frontend
cd frontend && npx next build

# Générer requirements.txt
python manage.py generate_requirements
```

## 🔗 API

Documentation interactive disponible après démarrage du backend:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/

20 routeurs API organisés par domaine: auth, recettes, courses, inventaire, planning, suggestions IA, famille, maison, jeux, dashboard, batch-cooking, anti-gaspillage, préférences, export PDF, calendriers, documents, utilitaires, push, webhooks, upload.

## 📚 Documentation complémentaire

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — Architecture détaillée
- [API_REFERENCE.md](docs/API_REFERENCE.md) — Référence API
- [SERVICES_REFERENCE.md](docs/SERVICES_REFERENCE.md) — Référence services
- [frontend/README.md](frontend/README.md) — Documentation frontend Next.js
- [ROADMAP.md](ROADMAP.md) — Roadmap et TODO
- [.github/copilot-instructions.md](.github/copilot-instructions.md) — Guide développeur Copilot

## 📄 Licence

Projet privé — Usage familial uniquement.