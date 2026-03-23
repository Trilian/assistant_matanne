# Instructions Copilot pour Codebase Assistant Matanne

## Vue d'ensemble du projet

**Type**: Application web de gestion familiale (FastAPI + Next.js)
**Backend**: Python 3.13+, FastAPI, SQLAlchemy 2.0 ORM, Pydantic v2
**Frontend**: Next.js 16.2.1, TypeScript 5, Tailwind CSS v4, shadcn/ui
**Base de données**: Supabase PostgreSQL avec migrations SQL-file
**Stack clé**: FastAPI, SQLAlchemy, Pydantic, Mistral AI, TanStack Query, Zustand, Zod

Hub de gestion familiale en production avec modules pour:

- 🍽️ Recettes et planification des repas (suggestions IA)
- 🛍️ Listes de courses et scans de codes-barres
- 📅 Planification d'activités et routines familiales
- 👶 Suivi du développement de l'enfant (Jules)
- 🏡 Gestion de la maison (projets, jardin, entretien, énergie)
- 🎮 Jeux (paris sportifs, loto)
- 📊 Tableau de bord familial avec métriques

**Architecture**: API REST FastAPI (backend Python) + SPA Next.js 16 (App Router, Turbopack). Modèles SQLAlchemy modulaires dans `core/models/` (22 fichiers). Codebase en français (noms variables, commentaires, docstrings). Marqueur `py.typed` (PEP 561).

---

## Architecture

### Vue d'ensemble

```
assistant_matanne/
├── frontend/               # Next.js 16 (React/TypeScript)
│   ├── src/app/(app)/      # Routes par module (~42 pages)
│   ├── src/components/     # Composants shadcn/ui (21+)
│   ├── src/composants/     # Composants layout (sidebar, header, nav)
│   ├── src/lib/api/        # Clients API par domaine
│   ├── src/hooks/          # Custom hooks React
│   ├── src/stores/         # Zustand stores
│   ├── src/types/          # Interfaces TypeScript
│   └── src/fournisseurs/   # Providers (auth, query, theme)
├── src/                    # Backend Python (FastAPI)
│   ├── api/                # API FastAPI (REST, routes, schemas, middleware)
│   ├── core/               # Noyau partagé (config, DB, models, AI, cache)
│   └── services/           # Logique métier
├── sql/                    # Schéma DB + migrations
├── tests/                  # Tests Python (pytest)
├── data/                   # Données statiques (JSON, CSV)
└── docs/                   # Documentation
```

### API FastAPI (src/api/)

Point d'entrée: `src/api/main.py` — Application FastAPI avec middlewares et routers.

- **main.py**: App FastAPI, CORS, middlewares (rate limiting, versioning, ETag, metrics, security headers), exception handler global, health checks
- **routes/**: 20 routeurs par domaine — chaque fichier exporte un `router = APIRouter(prefix="/api/v1/...")`:
  - `auth.py`: Authentification JWT (login, refresh, me)
  - `recettes.py`, `courses.py`, `inventaire.py`, `planning.py`: CRUD cuisine
  - `suggestions.py`: Suggestions IA via Mistral
  - `famille.py`: Profils enfants, activités, jalons, budget
  - `maison.py`: Projets, routines, entretien, jardin, stocks
  - `jeux.py`: Paris sportifs, loto, equipes
  - `dashboard.py`: Données agrégées tableau de bord
  - `batch_cooking.py`, `anti_gaspillage.py`, `preferences.py`: Modules spécialisés
  - `export.py`: Export PDF (courses, planning, recettes, budget)
  - `calendriers.py`, `documents.py`, `utilitaires.py`: Modules support
  - `push.py`, `webhooks.py`, `upload.py`: Notifications, webhooks, fichiers
- **schemas/**: Schémas Pydantic de validation/sérialisation — `base.py` (mixins), `common.py` (ErrorResponse, ReponsePaginee, MessageResponse), un fichier par domaine
- **dependencies.py**: Dépendances FastAPI centralisées (`require_auth`, `require_role`, `get_current_user`) via JWT Bearer
- **auth.py**: Module auth autonome (création/validation tokens JWT)
- **rate_limiting/**: Middleware de limitation de débit (60 req/min standard, 10 req/min IA)
- **versioning.py**: Versioning API (v1/v2), préfixes centralisés (`API_V1_PREFIX = "/api/v1"`)
- **utils/**: Helpers (`gerer_exception_api`, `executer_async`, `executer_avec_session`, `construire_reponse_paginee`), middlewares (ETag, Metrics, SecurityHeaders)
- **pagination.py**: Pagination cursor-based
- **websocket_courses.py**: WebSocket pour collaboration temps réel sur les listes de courses
- **prometheus.py**: Métriques Prometheus

### Noyau partagé (src/core/)

Le core est organisé en **10 sous-packages** + fichiers utilitaires.

- **ai/**: `ClientIA` (client Mistral), `AnalyseurIA` (parsing JSON/Pydantic), `CacheIA` (cache sémantique), `RateLimitIA` (rate limiting), `CircuitBreaker` (résilience API)
- **caching/**: Cache multi-niveaux — `base.py` (types), `memory.py` (L1), `file.py` (L3), `orchestrator.py` (CacheMultiNiveau, obtenir_cache). Décorateur unifié `@avec_cache`
- **config/**: Pydantic `BaseSettings` — `settings.py` (Parametres, obtenir_parametres), `loader.py` (chargement .env), `validator.py` (ValidateurConfiguration)
- **date_utils/**: Package utilitaires de dates — `semaines.py`, `periodes.py`, `formatage.py`, `helpers.py`. Re-exports transparents via `__init__.py`.
- **db/**: Base de données — `engine.py` (Engine SQLAlchemy, QueuePool), `session.py` (context managers), `migrations.py` (GestionnaireMigrations SQL-file), `utils.py` (health checks)
- **decorators/**: Package décorateurs — `db.py` (`@avec_session_db`), `cache.py` (`@avec_cache`), `errors.py` (`@avec_gestion_erreurs`), `validation.py` (`@avec_validation`, `@avec_resilience`)
- **models/**: Modèles SQLAlchemy ORM modulaires (22 fichiers organisés par domaine)
- **monitoring/**: Métriques & performance — `collector.py`, `decorators.py`, `health.py`
- **observability/**: Contexte d'observabilité — `context.py`
- **resilience/**: Politiques de résilience composables — `policies.py`. `executer()` retourne `T` directement ou lève une exception.
- **validation/**: Package validation — `schemas/` (sous-package Pydantic: `recettes.py`, `inventaire.py`, `courses.py`, `planning.py`, `famille.py`, `projets.py`, `_helpers.py`), `sanitizer.py` (anti-XSS/injection), `validators.py` (helpers)
- **Utilitaires**: `bootstrap.py` (init config + events), `constants.py`, `exceptions.py` (exceptions pures sans UI), `logging.py`, `async_utils.py`, `py.typed`

### Couche Services (src/services/)

- **core/base/**: `BaseAIService` (dans `ai_service.py`) avec limitation de débit intégrée, cache sémantique, parsing JSON, mixins IA, streaming, protocols, pipeline
- **core/registry.py**: Registre de services avec décorateur `@service_factory` pour singletons
- **core/events/**: Bus d'événements pub/sub avec wildcards
- **famille/**: Services IA famille — `jules_ai.py` (JulesAIService), `weekend_ai.py` (WeekendAIService)
- **cuisine/**: Service recettes avec `importer.py` pour import URL/PDF
- **planning/**: Service modulaire divisé en sous-modules:
  - `nutrition.py`: Équilibre nutritionnel
  - `agregation.py`: Agrégation des courses
  - `formatters.py`: Formatage pour l'API
  - `validators.py`: Validation des plannings
  - `prompts.py`: Génération de prompts IA
- **inventaire/**: Service de gestion des stocks
- **jeux/**, **maison/**: Services spécifiques au domaine
- **rapports/**: Génération PDF
- **utilitaires/**: Services utilitaires divers
- **integrations/**: Intégrations externes
- **webhooks.py**, **multimodal.py**, **profils.py**: Services support
- Tous exportent des fonctions factory `get_{service_name}_service()` décorées avec `@service_factory` pour le singleton via registre

### Frontend Next.js (frontend/)

- **App Router** (`src/app/`): Layout racine avec providers → `(auth)/` pour connexion/inscription, `(app)/` pour l'app protégée
- **Pages par module** (`src/app/(app)/`):
  - `page.tsx`: Tableau de bord (dashboard)
  - `cuisine/`: Hub + recettes, planning, courses, inventaire, anti-gaspillage, batch-cooking
  - `famille/`: Hub + jules, activites, routines, budget, weekend, album, anniversaires, contacts, documents, journal
  - `maison/`: Hub + projets, charges, depenses, energie, entretien, jardin, stocks
  - `planning/`: Hub + timeline
  - `jeux/`: Hub + paris, loto, euromillions
  - `outils/`: Hub + chat-ia, convertisseur, meteo, minuteur, notes
  - `parametres/`: Page paramètres
- **Composants** (`src/components/ui/`): 21+ composants shadcn/ui (button, card, input, dialog, tabs, table, sidebar, etc.)
- **Layout** (`src/composants/disposition/`): `coquille-app.tsx` (wrapper principal), `barre-laterale.tsx` (sidebar), `en-tete.tsx` (header), `nav-mobile.tsx` (bottom bar), `fil-ariane.tsx` (breadcrumbs)
- **API Clients** (`src/lib/api/`): Un client par domaine (`recettes.ts`, `courses.ts`, `inventaire.ts`, `planning.ts`, `famille.ts`, `maison.ts`, `jeux.ts`, `auth.ts`, `tableau-bord.ts`) + `client.ts` (instance Axios avec intercepteurs JWT)
- **Hooks** (`src/hooks/`): `utiliser-auth.ts`, `utiliser-api.ts` (wrappers TanStack Query), `utiliser-stockage-local.ts`, `utiliser-delai.ts`, `use-mobile.ts`
- **Stores** (`src/stores/`): Zustand — `store-auth.ts` (user/login), `store-ui.ts` (sidebar/search), `store-notifications.ts` (toasts)
- **Types** (`src/types/`): Interfaces TypeScript par domaine (`api.ts`, `recettes.ts`, `courses.ts`, `inventaire.ts`, `planning.ts`, `famille.ts`, `maison.ts`, `jeux.ts`)
- **Providers** (`src/fournisseurs/`): `fournisseur-query.tsx` (TanStack Query), `fournisseur-auth.tsx` (route protection), `fournisseur-theme.tsx` (next-themes)
- **Validation**: Zod 4.3.6 (`src/lib/validateurs.ts`)
- **Stack**: TanStack Query v5 (data fetching), Zustand 5 (state), react-hook-form 7.72 (forms), Zod (validation), Tailwind CSS v4

---

## Flux de travail critiques pour les développeurs

### Lancer l'application

```bash
# Backend FastAPI (depuis la racine)
python manage.py run
# ou directement:
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend Next.js (dans un autre terminal)
cd frontend
npm run dev          # http://localhost:3000

# Les deux en parallèle pour le développement complet
```

### Base de données

```bash
# Initialisation complète du schéma (tables, RLS, triggers, vues)
# Exécuter sql/INIT_COMPLET.sql dans Supabase SQL Editor ou psql

# Vérifier la connexion
python -c "from src.core.db import obtenir_moteur; obtenir_moteur().connect()"

# Créer une migration SQL
python manage.py create-migration

# Appliquer les migrations en attente
python manage.py migrate
```

### Tests

```bash
# Tests Python — tous les tests avec rapport de couverture
python manage.py test_coverage
# Exécute: pytest --cov=src --cov-report=html --cov-report=term

# Tests Python — fichier spécifique
pytest tests/test_recettes.py -v

# Tests Python — test unique
pytest tests/test_recettes.py::TestRecette::test_create -v

# Tests Frontend — Vitest
cd frontend && npm test

# Tests E2E — Playwright
cd frontend && npx playwright test
```

### Qualité du code

```bash
# Backend: formater (black)
python manage.py format_code

# Backend: linter (ruff)
python manage.py lint

# Frontend: linter (ESLint)
cd frontend && npm run lint

# Frontend: build de vérification
cd frontend && npx next build

# Générer requirements.txt depuis pyproject.toml
python manage.py generate_requirements
```

---

## Conventions spécifiques au projet

### Nommage et langage

- **Français partout** (backend): Tous les noms de variables, commentaires, docstrings et noms de fonctions Python utilisent le français (ex: `obtenir_parametres()`, `GestionnaireMigrations`, `avec_session_db`)
- **Frontend mixte**: Code en français (noms de variables, hooks comme `utiliser-auth.ts`, stores comme `store-auth.ts`), noms de composants shadcn/ui en anglais
- **Structure backend**: Modèles SQLAlchemy dans `src/core/models/` (22 fichiers modulaires), décorateurs dans `src/core/decorators/`, utilitaires dans `src/core/`
- **Structure API**: Routes dans `src/api/routes/`, schémas Pydantic dans `src/api/schemas/`, un fichier par domaine
- **Factories de services**: Toujours exporter une fonction `get_{service_name}_service()` décorée avec `@service_factory` pour le singleton via registre
- **Frontend pages**: `frontend/src/app/(app)/{module}/page.tsx` pour chaque page

### API REST Pattern

Chaque route suit le pattern standardisé:

```python
# src/api/routes/recettes.py
from fastapi import APIRouter, Depends, Query
from src.api.dependencies import require_auth
from src.api.schemas import RecetteCreate, RecetteResponse, ReponsePaginee
from src.api.schemas.errors import REPONSES_CRUD_CREATION, REPONSES_LISTE
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/recettes", tags=["Recettes"])

@router.get("", response_model=ReponsePaginee[RecetteResponse], responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_recettes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: dict = Depends(require_auth),
) -> dict:
    def _query():
        with executer_avec_session() as session:
            # Logique DB ici
            ...
    return await executer_async(_query)
```

Clé: Toujours utiliser `@gerer_exception_api` + `Depends(require_auth)` + `executer_avec_session()` pour les accès DB.

### Modèle de gestion des erreurs

```python
# Backend/services (pas de dépendance UI)
from src.core.exceptions import ErreurBaseDeDonnees

# Routes FastAPI (réponses HTTP standardisées)
from fastapi import HTTPException

try:
    result = perform_operation()
except Exception as e:
    logger.error(f"L'opération a échoué: {e}")
    raise HTTPException(status_code=500, detail="Message convivial pour l'utilisateur")
```

Le gestionnaire `@gerer_exception_api` capture les exceptions non gérées et retourne des réponses JSON standardisées.

### Gestion des sessions de base de données

```python
from src.core.db import obtenir_contexte_db
from src.core.decorators import avec_session_db

# Modèle 1: Dans les routes FastAPI (préféré)
def _query():
    with executer_avec_session() as session:
        result = session.query(Recette).first()
        return {"id": result.id, "nom": result.nom}

# Modèle 2: Utiliser le décorateur (pour les services)
@avec_session_db
def create_recipe(data: dict, db: Session) -> Recette:
    recette = Recette(**data)
    db.add(recette)
    db.commit()
    return recette

# Modèle 3: Gestionnaire de contexte manuel (pour les flux complexes)
with obtenir_contexte_db() as session:
    result = session.query(Recette).first()
    session.commit()
```

Clé: Dans les routes FastAPI, utiliser `executer_avec_session()`. Dans les services, utiliser `@avec_session_db` ou `obtenir_contexte_db()`. Ne jamais créer Engine/Session directement.

### Stratégie de cache

- **Cache multi-niveaux unifié**: `@avec_cache(ttl=300)` dans `src/core/decorators/cache.py` — délègue à `CacheMultiNiveau` (L1 mémoire → L3 fichier)
- **Cache des réponses IA**: `CacheIA` dans `src/core/ai/cache.py` pour le cache sémantique des appels IA
- **Cache HTTP**: Middleware ETag dans `src/api/utils/` pour le cache côté client
- **Cache Frontend**: TanStack Query gère le cache côté client (staleTime, gcTime)
- **Invalidation manuelle**: `Cache.invalider(pattern="prefix_")` ou `cache.invalider_par_tag("tag")`

> **Règle**: Utiliser `@avec_cache` dans les services/métier. Le cache HTTP (ETag) est géré automatiquement par le middleware.

### Authentification

- **Backend**: JWT Bearer tokens via `src/api/auth.py` et `src/api/dependencies.py`
- **Frontend**: Intercepteurs Axios dans `src/lib/api/client.ts` ajoutent le token automatiquement
- **Protection de routes**: `Depends(require_auth)` sur chaque endpoint, `fournisseur-auth.tsx` côté frontend
- **Mode dev**: Auto-auth avec utilisateur dev si `ENVIRONMENT=development`

### Résilience des appels externes

Tous les appels HTTP/API externes doivent utiliser `@avec_resilience`:

```python
from src.core.decorators import avec_resilience

@avec_resilience(retry=2, timeout_s=30, fallback=None)
def appel_api_externe():
    return httpx.get("https://api.example.com").json()
```

### Service Factory Pattern

Tous les services singleton utilisent `@service_factory` du registre:

```python
from src.services.core.registry import service_factory

@service_factory("mon_service", tags={"domaine"})
def get_mon_service() -> MonService:
    return MonService()
```

---

## Points d'intégration et dépendances

### APIs externes

- **Mistral AI**: Client à `src/core/ai/client.py`, configuré dans `src/core/config/`. Tous les appels IA passent par `BaseAIService` avec limitation de débit et cache intégrés.
- **Supabase PostgreSQL**: Connexion via `DATABASE_URL` depuis `.env.local`. Format: `postgresql://user:password@host/db`
- **Supabase Auth**: Authentification utilisateur via Supabase GoTrue, tokens JWT API créés côté backend
- **Limites de débit**: `AI_RATE_LIMIT_DAILY`, `AI_RATE_LIMIT_HOURLY` définis dans `src/core/constants.py`. Rate limiting API: 60 req/min standard, 10 req/min IA.

### Intégration du service IA

```python
from src.services.core.base import BaseAIService
from src.core.ai import ClientIA, AnalyseurIA

class MonService(BaseAIService):
    def suggest_recipes(self, context: str) -> list[Recette]:
        """Intégration IA avec limitation de débit & cache automatiques"""
        return self.call_with_list_parsing_sync(
            prompt=f"Suggère des recettes pour: {context}",
            item_model=Recette,
            system_prompt="Tu es un expert culinaire..."
        )

# Utilisation:
service = get_recette_service()  # Fonction factory
suggestions = service.suggest_recipes("Dîner rapide")
```

### Communication Frontend ↔ Backend

- **API Clients**: Chaque domaine a son client dans `frontend/src/lib/api/` utilisant l'instance Axios centralisée avec intercepteurs JWT
- **Data Fetching**: TanStack Query v5 pour le fetching et le cache côté client via les hooks dans `frontend/src/hooks/utiliser-api.ts`
- **State Management**: Zustand stores pour l'état local (auth, UI, notifications)
- **Validation**: Zod côté frontend, Pydantic côté backend — schémas miroir
- **WebSocket**: Collaboration temps réel sur les courses via `src/api/websocket_courses.py`

### Sources de configuration (en cascade)

1. Variables d'environnement système (plus haute priorité)
2. Fichier `.env.local` (racine du projet)
3. Fichier `.env` (fallback)
4. Valeurs par défaut codées en dur dans `src/core/constants.py`

Importer via: `from src.core.config import obtenir_parametres()`

---

## Modèles courants à suivre

### Ajouter une route API

1. Créer le schéma Pydantic dans `src/api/schemas/mondomaine.py`:
   ```python
   from pydantic import BaseModel, Field

   class MonItemCreate(BaseModel):
       nom: str = Field(..., description="Nom de l'item")

   class MonItemResponse(BaseModel):
       id: int
       nom: str
   ```

2. Créer le routeur dans `src/api/routes/mondomaine.py`:
   ```python
   from fastapi import APIRouter, Depends, Query
   from src.api.dependencies import require_auth
   from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

   router = APIRouter(prefix="/api/v1/mondomaine", tags=["MonDomaine"])

   @router.get("", response_model=ReponsePaginee[MonItemResponse])
   @gerer_exception_api
   async def lister_items(
       page: int = Query(1, ge=1),
       user: dict = Depends(require_auth),
   ) -> dict:
       def _query():
           with executer_avec_session() as session:
               items = session.query(MonModele).all()
               return construire_reponse_paginee(items, page, 20)
       return await executer_async(_query)
   ```

3. Enregistrer le routeur dans `src/api/routes/__init__.py` et `src/api/main.py`:
   ```python
   # Dans routes/__init__.py
   from .mondomaine import router as mondomaine_router

   # Dans main.py
   app.include_router(mondomaine_router)
   ```

### Ajouter un modèle de base de données

1. Ajouter la classe dans le fichier approprié sous `src/core/models/` en héritant de `Base`
2. Suivre les modèles ORM SQLAlchemy 2.0 avec `mapped_column` et `Mapped`
3. Utiliser la convention de nommage pour les contraintes (déjà configurée)
4. Ajouter le CREATE TABLE dans `sql/INIT_COMPLET.sql`
5. Ajouter RLS et triggers dans les sections correspondantes
6. Créer le schéma Pydantic correspondant dans `src/api/schemas/`

### Ajouter une page frontend

1. Créer `frontend/src/app/(app)/monmodule/page.tsx`:
   ```tsx
   'use client'

   export default function MonModulePage() {
     return (
       <div className="space-y-6">
         <h1 className="text-2xl font-bold">Mon Module</h1>
         {/* Contenu */}
       </div>
     )
   }
   ```

2. Ajouter le client API dans `frontend/src/lib/api/monmodule.ts`:
   ```typescript
   import { apiClient } from './client'

   export async function listerItems(page = 1) {
     const { data } = await apiClient.get('/api/v1/mondomaine', { params: { page } })
     return data
   }
   ```

3. Ajouter les types dans `frontend/src/types/monmodule.ts`
4. Ajouter le lien dans la barre latérale (`src/composants/disposition/barre-laterale.tsx`)

### Intégration IA

```python
from src.services.core.base import BaseAIService
from src.core.ai import ClientIA

class RecipeService(BaseAIService):
    """Service avec intégration IA automatique"""

    def generate_shopping_list(self, recipes: list[Recette]) -> list[dict]:
        """Générer la liste à partir des recettes — limitation de débit automatique"""
        prompt = f"Créer liste courses pour: {recipes}"

        # Gère automatiquement: limitation de débit, cache, parsing, récupération d'erreurs
        return self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=ArticleCourses,
            system_prompt="Tu es expert en gestion courses..."
        )
```

### Modèles de test

```python
# Backend: dans tests/test_mymodule.py
import pytest
from sqlalchemy.orm import Session

@pytest.mark.unit
def test_create_recipe(test_db: Session):
    """Tester l'opération de base de données avec fixture"""
    from src.services.cuisine import RecetteService

    service = RecetteService(test_db)
    result = service.creer_recette({"nom": "Tarte"})

    assert result.nom == "Tarte"
    # Session nettoyée automatiquement après le test
```

```typescript
// Frontend: dans frontend/src/**/*.test.ts
import { describe, it, expect } from 'vitest'

describe('listerRecettes', () => {
  it('retourne une liste paginée', async () => {
    // ...
  })
})
```

Clé: `conftest.py` fournit des fixtures de base de données SQLite en mémoire pour des tests isolés.

---

## Référence des fichiers clés

### Backend

| Fichier | Objectif |
| --- | --- |
| `src/api/main.py` | App FastAPI principale, middlewares, health checks |
| `src/api/routes/` | 20 routeurs API par domaine |
| `src/api/schemas/` | Schémas Pydantic de validation/sérialisation |
| `src/api/dependencies.py` | Auth dependencies (require_auth, require_role) |
| `src/api/auth.py` | Création/validation tokens JWT |
| `src/api/rate_limiting/` | Middleware limitation de débit |
| `src/api/utils/` | Helpers API, middlewares (ETag, Metrics, Security) |
| `src/api/versioning.py` | Versioning API (v1/v2) |
| `src/core/config/` | Package configuration (Pydantic BaseSettings) |
| `src/core/db/` | Package base de données (engine, sessions, migrations) |
| `src/core/caching/` | Package cache multi-niveaux (L1/L3, @avec_cache) |
| `src/core/ai/` | Package IA (Mistral, rate limiting, cache, circuit breaker) |
| `src/core/models/` | Tous les modèles ORM SQLAlchemy (22 fichiers) |
| `src/core/decorators/` | Décorateurs (@avec_session_db, @avec_cache, etc.) |
| `src/core/resilience/` | Politiques de résilience composables |
| `src/core/validation/` | Validation (schemas/ sous-package, sanitizer) |
| `src/core/monitoring/` | Métriques & performance |
| `src/services/core/registry.py` | Registre de services + @service_factory |
| `src/services/core/base/` | BaseAIService, mixins IA, streaming, protocols |
| `pyproject.toml` | Dépendances Python, config test, règles de linting |

### Frontend

| Fichier | Objectif |
| --- | --- |
| `frontend/src/app/(app)/layout.tsx` | Layout app avec sidebar/nav |
| `frontend/src/app/(app)/page.tsx` | Dashboard principal |
| `frontend/src/lib/api/client.ts` | Instance Axios + intercepteurs JWT |
| `frontend/src/lib/api/` | Clients API par domaine |
| `frontend/src/hooks/` | Custom hooks React (auth, api, etc.) |
| `frontend/src/stores/` | Zustand stores (auth, UI, notifications) |
| `frontend/src/types/` | Interfaces TypeScript par domaine |
| `frontend/src/composants/disposition/` | Layout components (sidebar, header, nav) |
| `frontend/src/components/ui/` | Composants shadcn/ui (21+) |
| `frontend/src/fournisseurs/` | Providers (TanStack Query, auth, theme) |
| `frontend/src/lib/validateurs.ts` | Schémas de validation Zod |
| `frontend/package.json` | Dépendances frontend, scripts npm |

---

## Débogage rapide

**API ne démarre pas?**

- Vérifier les imports dans `src/api/main.py` et `src/api/routes/__init__.py`
- Lancer `uvicorn src.api.main:app --reload` et vérifier les erreurs
- Vérifier les dépendances: `pip install -r requirements.txt`
- Documentation interactive: `http://localhost:8000/docs`

**Connexion DB échouée?**

- Vérifier `DATABASE_URL` dans `.env.local`: format `postgresql://user:pass@host/db`
- Tester: `python -c "from src.core.db import obtenir_moteur; obtenir_moteur().connect()"`

**Tests échouent?**

- `conftest.py` fournit des fixtures SQLite en mémoire pour tests isolés
- Test unique: `pytest tests/test_name.py::TestClass::test_method -v`
- Supprimer `__pycache__/` après un refactoring pour éviter les `.pyc` obsolètes
- Tests frontend: `cd frontend && npm test`

**Migrations ne s'appliquent pas?**

- Vérifier `sql/migrations/` pour les erreurs de syntaxe SQL
- Vérifier la table `schema_migrations` dans la base
- Exécuter `python manage.py migrate` pour voir les détails

**Frontend ne se connecte pas à l'API?**

- Vérifier que le backend tourne sur `http://localhost:8000`
- Vérifier les CORS dans `src/api/main.py` (localhost:3000 autorisé par défaut)
- Vérifier `NEXT_PUBLIC_API_URL` dans `frontend/.env.local`
- Inspecter l'onglet Network du navigateur pour les erreurs 401/403/CORS

**Auth échoue?**

- Mode dev: `ENVIRONMENT=development` active l'auto-auth
- Production: Vérifier la config Supabase Auth et les variables JWT
- Vérifier le header `Authorization: Bearer <token>`