# 🏗️ Architecture Technique - Assistant Matanne

> **Dernière mise à jour**: 1 mars 2026

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                     NEXT.JS 16 FRONTEND                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │Dashboard │ │ Cuisine  │ │ Famille  │ │ Maison   │ ...       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
│       │            │            │            │                   │
│       └────────────┴─────┬──────┴────────────┘                  │
│                          │                                       │
│        App Router + TanStack Query + Zustand + shadcn/ui        │
└──────────────────────────┼───────────────────────────────────────┘
                           │  REST API (HTTP/WS)
┌──────────────────────────┼───────────────────────────────────────┐
│                      FASTAPI BACKEND                             │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │  Auth   │ │  Routes  │ │ Schemas  │ │Middleware│            │
│  │  JWT    │ │  (20+)   │ │ Pydantic │ │(CORS,RL)│            │
│  └────┬────┘ └────┬─────┘ └────┬─────┘ └────┬────┘            │
└───────┼───────────┼────────────┼────────────┼────────────────────┘
        │           │            │            │
┌───────┼───────────┼────────────┼────────────┼────────────────────┐
│                     SERVICES LAYER                               │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │  Cuisine   │ │  Famille   │ │  Maison    │ │  Jeux      │   │
│  │ (recettes, │ │            │ │ (entretien)│ │ (loto,     │   │
│  │  courses)  │ │            │ │            │ │  paris)    │   │
│  └──────┬─────┘ └──────┬─────┘ └──────┬─────┘ └──────┬─────┘   │
│         │              │              │              │           │
│         └──────────────┴──────┬───────┴──────────────┘          │
│                               │                                  │
│                   services/core/base/                            │
│              BaseAIService, CQRS, Events,                       │
│              Notifications, Backup, Observability                │
└───────────────────────────────┼──────────────────────────────────┘
                                │
┌───────────────────────────────┼──────────────────────────────────┐
│                          CORE LAYER                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Database │  │ Models   │  │   AI     │  │  Cache   │        │
│  │ (Pool)   │  │ (ORM 22) │  │ (Mistral)│  │ (3 niv.) │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Result   │  │Resilience│  │Middleware│  │  State   │        │
│  │ (Monad)  │  │(policies)│  │(pipeline)│  │ (slices) │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Validat° │  │DateUtils │  │  Config  │  │ Monitor  │        │
│  │ (schemas)│  │(package) │  │(Pydantic)│  │ (health) │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
└───────┼─────────────┼─────────────┼─────────────┼────────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌───────────────┐ ┌─────────┐ ┌───────────┐
│   Supabase    │ │  SQLAlch│ │  Mistral  │
│  PostgreSQL   │ │  ORM 2.0│ │    API    │
└───────────────┘ └─────────┘ └───────────┘
```

## Modules Core (src/core/)

Le core est organisé en **10 sous-packages** + fichiers utilitaires:

```
src/core/
├── ai/              # Client Mistral, cache sémantique, rate limiting, circuit breaker
├── ai/              # Client Mistral, analyseur, cache sémantique, rate limiting, circuit breaker
├── caching/         # Cache multi-niveaux L1/L3 (décorateur unifié @avec_cache)
├── config/          # Pydantic BaseSettings, chargement .env, validateur
├── date_utils/      # Package utilitaires de dates (4 modules)
├── db/              # Engine, sessions, migrations SQL-file
├── decorators/      # Package: cache.py, db.py, errors.py, validation.py
├── dto/             # Data Transfer Objects
├── models/          # 22+ modèles SQLAlchemy ORM
├── monitoring/      # Collecteur métriques, health checks
├── observability/   # Contexte d'observabilité (spans, traces)
├── resilience/      # Politiques de résilience composables (retry, timeout, bulkhead)
├── utils/           # Utilitaires partagés
├── validation/      # Schemas Pydantic (7 domaines), sanitizer
├── async_utils.py   # Utilitaires asynchrones
├── bootstrap.py     # demarrer_application() — initialisation IoC
├── constants.py     # Constantes globales
├── exceptions.py    # Exceptions métier (ErreurBaseDeDonnees, etc.)
├── logging.py       # Configuration logging
└── py.typed         # Marqueur PEP 561 pour typing
```

### config/ — Configuration centralisée

```python
# Pydantic BaseSettings avec chargement en cascade:
# .env.local → .env → variables d'environnement → constantes
from src.core.config import obtenir_parametres
config = obtenir_parametres()
```

Fichiers: `settings.py` (Parametres), `loader.py` (chargement .env), `validator.py` (ValidateurConfiguration)

### db/ — Base de données

```python
# Connexion avec QueuePool (5 connexions, max 10)
from src.core.db import obtenir_contexte_db

with obtenir_contexte_db() as session:
    result = session.query(Recette).all()
```

Fichiers: `engine.py`, `session.py`, `migrations.py` (SQL-file based, post-Alembic), `utils.py`

**Migrations SQL**: Les migrations sont des fichiers `.sql` numérotés dans `sql/migrations/`.
Le système suit les versions appliquées dans la table `schema_migrations` avec checksums SHA-256.

### caching/ — Cache multi-niveaux

```python
from src.core.decorators import avec_cache

# Décorateur unifié — délègue à CacheMultiNiveau (L1→L2→L3)
@avec_cache(ttl=300)
def get_recettes(): ...
```

Fichiers: `base.py` (types), `memory.py` (L1), `session.py` (L2), `file.py` (L3), `orchestrator.py`, `cache.py`

> **Note**: Les anciens décorateurs `@cached` et `@avec_cache_multi` ont été supprimés.
> Seul `@avec_cache` (dans `decorators.py`) est utilisé — il passe par `CacheMultiNiveau` automatiquement.

### date_utils/ — Utilitaires de dates (package)

```python
from src.core.date_utils import obtenir_debut_semaine, formater_date_fr, plage_dates
```

| Module         | Fonctions                                                                         |
| -------------- | --------------------------------------------------------------------------------- |
| `semaines.py`  | `obtenir_debut_semaine`, `obtenir_fin_semaine`, `obtenir_semaine_courante`        |
| `periodes.py`  | `plage_dates`, `ajouter_jours_ouvres`, `obtenir_bornes_mois`, `obtenir_trimestre` |
| `formatage.py` | `formater_date_fr`, `formater_jour_fr`, `formater_mois_fr`, `format_week_label`   |
| `helpers.py`   | `est_aujourd_hui`, `est_weekend`, `get_weekday_index`, `get_weekday_name`         |

### validation/ — Validation & sanitization

```
src/core/validation/
├── schemas/          # Package Pydantic (7 modules par domaine)
│   ├── recettes.py   # RecetteInput, IngredientInput, EtapeInput
│   ├── inventaire.py # ArticleInventaireInput, IngredientStockInput
│   ├── courses.py    # ArticleCoursesInput
│   ├── planning.py   # RepasInput
│   ├── famille.py    # EntreeJournalInput, RoutineInput, TacheRoutineInput
│   ├── projets.py    # ProjetInput
│   └── _helpers.py   # nettoyer_texte (utilitaire partagé)
├── sanitizer.py      # NettoyeurEntrees (anti-XSS/injection SQL)
└── validators.py     # valider_modele(), valider_entree(), afficher_erreurs_validation()
```

### decorators/ — Décorateurs métier (package)

```python
from src.core.decorators import avec_session_db, avec_cache, avec_gestion_erreurs, avec_validation

@avec_session_db      # Injecte automatiquement Session (src/core/decorators/db.py)
@avec_cache(ttl=300)  # Cache multi-niveaux unifié L1→L2→L3 (src/core/decorators/cache.py)
@avec_gestion_erreurs # Gestion erreurs unifiée (src/core/decorators/errors.py)
@avec_validation      # Validation Pydantic automatique (src/core/decorators/validation.py)
```

### resilience/ — Politiques de résilience

```python
from src.core.resilience import RetryPolicy, TimeoutPolicy, politique_ia

politique = RetryPolicy(3) + TimeoutPolicy(30)
result = politique.executer(lambda: appel_risque())
```

### monitoring/ — Métriques & Performance

```python
from src.core.monitoring import CollecteurMetriques

# Métriques de performance et health checks
collecteur = CollecteurMetriques()
```

Fichiers: `collector.py`, `decorators.py`, `health.py`

### bootstrap.py — Initialisation

```python
from src.core.bootstrap import demarrer_application

# Appelé au démarrage dans src/api/main.py
demarrer_application()
```

### events — Bus d'événements

```python
from src.services.core.events.bus import obtenir_bus

bus = obtenir_bus()
bus.on("recette.creee", lambda data: logger.info(f"Recette: {data['nom']}"))
bus.emettre("recette.creee", {"nom": "Tarte"})
```

> **Note**: Le bus d'événements est dans `src/services/core/events/` (pas dans core/).
> Support wildcards (`*`, `**`), priorités, isolation d'erreurs.

### models/ — SQLAlchemy 2.0 ORM (22 fichiers)

| Fichier               | Domaine                                               |
| --------------------- | ----------------------------------------------------- |
| `base.py`             | Base déclarative, convention de nommage               |
| `recettes.py`         | Recette, Ingredient, EtapeRecette, RecetteIngredient  |
| `inventaire.py`       | ArticleInventaire, HistoriqueInventaire               |
| `courses.py`          | ArticleCourses, ModeleCourses                         |
| `planning.py`         | Planning, Repas, CalendarEvent                        |
| `famille.py`          | ChildProfile, Milestone, FamilyActivity, FamilyBudget |
| `sante.py`            | HealthRoutine, HealthObjective, HealthEntry           |
| `maison.py`           | Project, Routine, GardenItem                          |
| `finances.py`         | Depense, BudgetMensuelDB                              |
| `habitat.py`          | Modèles habitat/logement                              |
| `jardin.py`           | Modèles jardin (zones, plantes)                       |
| `jeux.py`             | Modèles jeux (loto, paris)                            |
| `calendrier.py`       | CalendrierExterne                                     |
| `notifications.py`    | PushSubscription, alertes                             |
| `batch_cooking.py`    | Sessions batch cooking                                |
| `temps_entretien.py`  | Tâches d'entretien maison                             |
| `systeme.py`          | Backup, configuration système                         |
| `users.py`            | Utilisateurs                                          |
| `user_preferences.py` | Préférences utilisateur                               |

### ai/ — Intelligence Artificielle

```python
from src.core.ai import ClientIA, AnalyseurIA, CacheIA, RateLimitIA
from src.core.ai import CircuitBreaker, avec_circuit_breaker, obtenir_circuit

# Utilisation via BaseAIService (recommandé)
from src.services.core.base import BaseAIService

class MonService(BaseAIService):
    def suggest(self, prompt: str) -> list:
        return self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=MonModel
        )
```

Fichiers: `client.py`, `parser.py`, `cache.py`, `rate_limit.py`, `circuit_breaker.py`

## Services (src/services/)

Les services sont organisés en sous-packages par domaine:

```
src/services/
├── core/               # Services transversaux
│   ├── base/           # BaseAIService, mixins IA, streaming, protocols, pipeline
│   ├── backup/         # Backup/restore système complet
│   ├── events/         # Bus d'événements (bus.py, events.py, subscribers.py)
│   ├── notifications/  # Web push, NTFY, templates, persistance
│   ├── observability/  # Health checks, métriques, spans
│   ├── utilisateur/    # Préférences, historique
│   └── registry.py     # Registre de services (@service_factory)
├── cuisine/            # Recettes, courses
├── dashboard/          # Données tableau de bord
├── famille/            # Services famille (Jules IA, weekend IA)
├── integrations/       # APIs externes (codes-barres, factures, Garmin, météo, images)
├── inventaire/         # Gestion des stocks
├── jeux/               # Loto, paris sportifs
├── maison/             # Entretien, dépenses, jardin, projets
├── planning/           # Planning repas (nutrition, agrégation, prompts, validators)
├── rapports/           # Export PDF, rapports budget/gaspillage
└── utilitaires/        # Services utilitaires divers
```

### BaseAIService (src/services/core/base/)

```python
from src.services.core.base import BaseAIService

class MonService(BaseAIService):
    def suggest(self, prompt: str) -> list:
        # Gère automatiquement: rate limiting, cache sémantique, parsing, recovery
        return self.call_with_list_parsing_sync(
            prompt=prompt, item_model=MonModel
        )
```

Fichiers clés: `ai_service.py`, `ai_mixins.py`, `ai_prompts.py`, `ai_streaming.py`, `protocols.py`, `pipeline.py`

Chaque service domaine exporte une fonction factory `get_{service_name}_service()`.

## Routing

Le routage est géré par FastAPI côté backend (20 routers dans `src/api/routes/`) et Next.js App Router côté frontend (`frontend/src/app/(app)/`).

```python
# src/api/routes/recettes.py
router = APIRouter(prefix="/api/v1/recettes", tags=["Recettes"])

@router.get("")
async def lister_recettes(user: dict = Depends(require_auth)):
    ...
```

**Performance**: ~60% d'accélération au démarrage grâce au chargement différé des routes.

**Bootstrap**: `src/api/main.py` initialise l'application FastAPI avec middlewares et routers.

## Modules Métier

Les modules sont organisés en 3 couches : routes API (`src/api/routes/`), services (`src/services/`), modèles ORM (`src/core/models/`).

| Module | Routes API | Services | Description |
|---|---|---|---|
| Cuisine | `recettes.py`, `courses.py`, `inventaire.py`, `planning.py`, `batch_cooking.py`, `anti_gaspillage.py` | `cuisine/`, `planning/` | Recettes, courses, stocks, planning repas |
| Famille | `famille.py` | `famille/` | Vie familiale, suivi enfant Jules, budget |
| Maison | `maison.py` | `maison/` | Habitat, entretien, jardin, dépenses |
| Jeux | `jeux.py` | `jeux/` | Paris sportifs, loto, euromillions |
| Planning | `planning.py`, `calendriers.py` | `planning/` | Calendrier, timeline |
| Dashboard | `dashboard.py` | `dashboard/` | Tableau de bord, métriques |
| Outils | `utilitaires.py`, `suggestions.py`, `export.py` | `utilitaires/`, `rapports/` | Chat IA, export PDF, outils divers |

## Frontend (frontend/src/)

```
frontend/src/
├── app/(app)/          # Routes Next.js par module (~50 pages)
├── app/(auth)/         # Pages connexion/inscription
├── composants/
│   ├── disposition/    # Layout (sidebar, header, nav-mobile, fil d'ariane)
│   └── ui/             # Composants shadcn/ui (button, card, dialog, table, etc.)
├── bibliotheque/api/   # Clients API par domaine (Axios)
├── crochets/           # Custom hooks React (auth, api, stockage-local, debounce)
├── magasins/           # Zustand stores (auth, ui, notifications)
├── types/              # Interfaces TypeScript par domaine
├── fournisseurs/       # Providers (TanStack Query, auth, thème)
└── middleware.ts       # Next.js middleware (auth route protection)
```

## Sécurité

### Row Level Security (RLS)

```sql
-- Supabase: chaque utilisateur voit ses données
CREATE POLICY depenses_user_policy ON depenses
    FOR ALL USING (user_id = auth.uid());
```

### Multi-tenant

> **Note**: Le module multi-tenant (`multi_tenant.py`) a été supprimé car inutilisé en production.
> L'isolation des données se fait via les politiques RLS de Supabase (voir ci-dessus).

## Cache

### Architecture multi-niveaux (src/core/caching/)

```
src/core/caching/
├── base.py          # EntreeCache, StatistiquesCache (types)
├── cache.py         # Cache simple (accès direct)
├── memory.py        # CacheMemoireN1 (L1: dict Python)
├── session.py       # CacheSessionN2 (L2: SessionStorage)
├── file.py          # CacheFichierN3 (L3: pickle sur disque)
└── orchestrator.py  # CacheMultiNiveau (orchestration L1→L2→L3)
```

1. **L1**: `CacheMemoireN1` — dict Python en mémoire (ultra rapide, volatile)
2. **L2**: `CacheSessionN2` — SessionStorage (persistant pendant la session)
3. **L3**: `CacheFichierN3` — pickle sur disque (persistant entre sessions)

```python
from src.core.decorators import avec_cache

# Décorateur unifié — délègue à CacheMultiNiveau
@avec_cache(ttl=300)
def get_recettes():
    ...

# Cache orchestrateur direct
from src.core.caching import obtenir_cache
cache = obtenir_cache()
cache.set("clé", valeur, ttl=600)
```

> **Note**: Un seul décorateur `@avec_cache` — les anciens `@cached` et `@avec_cache_multi` ont été supprimés.

### Cache sémantique IA

```python
from src.core.ai import CacheIA
# Cache les réponses IA par similarité sémantique
```

## Helpers Famille

Modules de logique pure extraits pour testabilité:

| Fichier              | Contenu                                                              |
| -------------------- | -------------------------------------------------------------------- |
| `age_utils.py`       | `get_age_jules()`, `_obtenir_date_naissance()` — calcul d'âge centralisé |
| `activites_utils.py` | Constantes (TYPES_ACTIVITE, LIEUX), filtrage, stats, recommandations |
| `routines_utils.py`  | Constantes (JOURS_SEMAINE, MOMENTS_JOURNEE), gestion du temps, stats |
| `utils.py`           | Helpers partagés avec `@avec_cache`                                  |

## Conventions

### Nommage (Français)

- Variables: `obtenir_recettes()`, `liste_courses`
- Classes: `GestionnaireMigrations`, `ArticleInventaire`
- Constantes: `CATEGORIES_DEPENSE`, `TYPES_REPAS`

### Structure fichiers

```python
"""
Docstring module
"""
import ...

# Types et schémas
class MonSchema(BaseModel): ...

# Service principal
class MonService:
    def methode(self): ...

# Factory (export)
def get_mon_service() -> MonService:
    return MonService()
```
