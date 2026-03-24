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

## 📚 Documentation

| Document | Description |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architecture technique détaillée |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | Référence complète de l'API REST |
| [SERVICES_REFERENCE.md](docs/SERVICES_REFERENCE.md) | Documentation des services backend |
| [FONCTIONNALITES.md](docs/FONCTIONNALITES.md) | Fonctionnalités détaillées par module |
| [ERD_SCHEMA.md](docs/ERD_SCHEMA.md) | Schéma entité-relation de la DB |
| [SQLALCHEMY_SESSION_GUIDE.md](docs/SQLALCHEMY_SESSION_GUIDE.md) | Guide sessions DB |
| [MIGRATION_CORE_PACKAGES.md](docs/MIGRATION_CORE_PACKAGES.md) | Guide migration imports core |
| [UI_COMPONENTS.md](docs/UI_COMPONENTS.md) | Composants UI Next.js / shadcn |
| [PATTERNS.md](docs/PATTERNS.md) | Patterns de code récurrents |
| [frontend/README.md](frontend/README.md) | Documentation frontend Next.js |
| [ROADMAP.md](ROADMAP.md) | Roadmap et historique des sprints |

---

## 📄 Licence

Projet privé — Usage familial uniquement.