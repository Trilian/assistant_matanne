# 🏗️ Architecture Technique - Assistant Matanne

> **Dernière mise à jour**: 19 Février 2026

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                        STREAMLIT UI                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ Accueil  │ │ Cuisine  │ │ Famille  │ │ Maison   │ ...       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
│       │            │            │            │                   │
│       └────────────┴─────┬──────┴────────────┘                  │
│                          │                                       │
│                    OptimizedRouter (lazy loading)                │
└──────────────────────────┼───────────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────────┐
│                     SERVICES LAYER                               │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │  Cuisine   │ │  Famille   │ │  Maison    │ │  Jeux      │   │
│  │ (recettes, │ │            │ │ (entretien)│ │ (loto,     │   │
│  │  courses)  │ │            │ │            │ │  paris)    │   │
│  └──────┬─────┘ └──────┬─────┘ └──────┬─────┘ └──────┬─────┘   │
│         │              │              │              │           │
│         └──────────────┴──────┬───────┴──────────────┘          │
│                               │                                  │
│                       BaseAIService                              │
│                    (rate limit, cache IA)                        │
└───────────────────────────────┼──────────────────────────────────┘
                                │
┌───────────────────────────────┼──────────────────────────────────┐
│                          CORE LAYER                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Database │  │ Models   │  │   AI     │  │  Cache   │        │
│  │ (Pool)   │  │ (ORM 19) │  │ (Mistral)│  │ (3 niv.) │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Validat° │  │DateUtils │  │  Config  │  │  State   │        │
│  │ (schemas)│  │(package) │  │(Pydantic)│  │ Manager  │        │
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

Le core est organisé en **7 sous-packages** + fichiers utilitaires:

```
src/core/
├── ai/              # Client Mistral, cache sémantique, rate limiting
├── caching/         # Cache multi-niveaux L1/L2/L3
├── config/          # Pydantic BaseSettings, chargement .env
├── date_utils/      # Package utilitaires de dates (4 modules)
├── db/              # Engine, sessions, migrations
├── models/          # 19 modèles SQLAlchemy ORM
├── validation/      # Schemas Pydantic (7 domaines), sanitizer
├── constants.py     # Constantes globales
├── decorators.py    # @with_db_session, @with_cache, @with_error_handling
├── errors.py        # Classes d'erreurs métier
├── errors_base.py   # Classe de base ErreurApplication
├── lazy_loader.py   # Import différé à la demande
├── logging.py       # Configuration logging
├── state.py         # StateManager (st.session_state)
└── py.typed         # Marqueur PEP 561 pour typing
```

### config/ — Configuration centralisée

```python
# Pydantic BaseSettings avec chargement en cascade:
# .env.local → .env → st.secrets → constantes
from src.core.config import obtenir_parametres
config = obtenir_parametres()
```

Fichiers: `settings.py` (Parametres), `loader.py` (chargement .env, secrets Streamlit)

### db/ — Base de données

```python
# Connexion avec QueuePool (5 connexions, max 10)
from src.core.db import obtenir_contexte_db

with obtenir_contexte_db() as session:
    result = session.query(Recette).all()
```

Fichiers: `engine.py`, `session.py`, `migrations.py`, `utils.py`

### caching/ — Cache multi-niveaux

```python
from src.core.caching import avec_cache_multi, obtenir_cache, cached

@avec_cache_multi(ttl=300, niveaux=["L1", "L2"])
def get_recettes(): ...

# Ou via le décorateur typé cached()
@cached(ttl=60)
def get_data(): ...
```

Fichiers: `base.py` (types), `memory.py` (L1), `session.py` (L2), `file.py` (L3), `orchestrator.py`, `cache.py`

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

### decorators.py

```python
@with_db_session      # Injecte automatiquement Session
@with_cache(ttl=300)  # Cache Streamlit 5 min
@with_error_handling  # Gestion erreurs unifiée
```

### models/ — SQLAlchemy 2.0 ORM (19 fichiers)

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

# Utilisation via BaseAIService (recommandé)
class MonService(BaseAIService):
    def suggest(self, prompt: str) -> list:
        return self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=MonModel
        )
```

## Services (src/services/)

Les services sont organisés en sous-packages par domaine:

```
src/services/
├── core/           # Services transversaux (utilisateur, historique)
├── cuisine/        # Recettes, courses, planning repas
├── famille/        # Services famille
├── integrations/   # Weather, APIs externes
├── inventaire/     # Gestion des stocks
├── jeux/           # Loto, paris sportifs
├── maison/         # Entretien, dépenses, schemas
└── rapports/       # Export PDF, rapports
```

Chaque service exporte une fonction factory `get_{service_name}_service()`.

## Lazy Loading (OptimizedRouter)

```python
# src/app.py
MODULE_REGISTRY = {
    "accueil": "src.modules.accueil",
    "cuisine": "src.modules.cuisine",
    "famille": "src.modules.famille",
    "maison":  "src.modules.maison",
    "jeux":    "src.modules.jeux",
    "planning": "src.modules.planning",
    "parametres": "src.modules.parametres",
    "utilitaires": "src.modules.utilitaires",
}

# Chaque module exporte app()
def app():
    """Point d'entrée module"""
    st.title("Mon Module")
```

**Performance**: ~60% d'accélération au démarrage

## Modules Métier (src/modules/)

Chaque module est un sous-package avec `__init__.py` exportant `app()`:

| Module         | Sous-modules                                                                                             | Description                               |
| -------------- | -------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| `accueil/`     | `dashboard.py`                                                                                           | Tableau de bord, métriques, alertes       |
| `cuisine/`     | `recettes/`, `courses/`, `inventaire/`, `planificateur_repas/`, `batch_cooking_detaille.py`              | Recettes, courses, stocks, planning repas |
| `famille/`     | `activites.py`, `routines.py`, `jules/`, `suivi_perso/`, `achats_famille/`, `weekend/`, `hub_famille.py` | Vie familiale, suivi enfant, santé        |
| `maison/`      | `entretien/`, `charges/`, `depenses/`, `jardin/`, `hub/`                                                 | Habitat, entretien, dépenses              |
| `jeux/`        | `loto/`, `paris/`                                                                                        | Loto, paris sportifs                      |
| `planning/`    | `calendrier/`, `timeline_ui.py`, `templates_ui.py`                                                       | Calendrier, timeline                      |
| `parametres/`  | `about.py`, `affichage.py`, `budget.py`, `cache.py`, `database.py`, `foyer.py`, `ia.py`                  | Réglages applicatifs                      |
| `utilitaires/` | `barcode.py`, `rapports.py`, `notifications_push.py`, `scan_factures.py`                                 | Outils transversaux                       |

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
├── cache.py         # Cache simple, décorateur @cached (typé ParamSpec)
├── memory.py        # CacheMemoireN1 (L1: dict Python)
├── session.py       # CacheSessionN2 (L2: st.session_state)
├── file.py          # CacheFichierN3 (L3: pickle sur disque)
└── orchestrator.py  # CacheMultiNiveau, @avec_cache_multi (typé ParamSpec)
```

1. **L1**: `CacheMemoireN1` — dict Python en mémoire (ultra rapide, volatile)
2. **L2**: `CacheSessionN2` — st.session_state (persistant pendant la session)
3. **L3**: `CacheFichierN3` — pickle sur disque (persistant entre sessions)

```python
from src.core.caching import avec_cache_multi, obtenir_cache

# Décorateur
@avec_cache_multi(ttl=300, niveaux=["L1", "L2"])
def get_recettes():
    ...

# Cache orchestrateur
cache = obtenir_cache()
cache.set("clé", valeur, ttl=600)
```

### Cache Redis (optionnel)

```python
from src.core.redis_cache import redis_cached

@redis_cached(ttl=3600, tags=["recettes"])
def get_recettes():
    ...
```

### Cache sémantique IA

```python
from src.core.ai import CacheIA
# Cache les réponses IA par similarité sémantique
```

## Helpers Famille

Modules de logique pure extraits pour testabilité:

| Fichier              | Contenu                                                              |
| -------------------- | -------------------------------------------------------------------- |
| `activites_utils.py` | Constantes (TYPES_ACTIVITE, LIEUX), filtrage, stats, recommandations |
| `routines_utils.py`  | Constantes (JOURS_SEMAINE, MOMENTS_JOURNEE), gestion du temps, stats |
| `utils.py`           | Helpers partagés avec `@st.cache_data`                               |

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
