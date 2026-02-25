# 🏗️ Architecture Technique - Assistant Matanne

> **Dernière mise à jour**: 25 Juin 2025

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
│              st.navigation() + ChargeurModuleDiffere            │
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
│                   services/core/base/                            │
│              BaseAIService, CQRS, Events,                       │
│              Notifications, Backup, Observability                │
└───────────────────────────────┼──────────────────────────────────┘
                                │
┌───────────────────────────────┼──────────────────────────────────┐
│                          CORE LAYER                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Database │  │ Models   │  │   AI     │  │  Cache   │        │
│  │ (Pool)   │  │ (ORM 19) │  │ (Mistral)│  │ (3 niv.) │        │
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

Le core est organisé en **14 sous-packages** + fichiers utilitaires:

```
src/core/
├── ai/              # Client Mistral, cache sémantique, rate limiting, circuit breaker
├── caching/         # Cache multi-niveaux L1/L2/L3 (décorateur unifié @avec_cache)
├── config/          # Pydantic BaseSettings, chargement .env, validateur
├── date_utils/      # Package utilitaires de dates (4 modules)
├── db/              # Engine, sessions, migrations SQL-file
├── decorators/      # Package: cache.py, db.py, errors.py, validation.py
├── middleware/      # Pipeline de middlewares composables (base, builtin, pipeline)
├── models/          # 19 modèles SQLAlchemy ORM
├── monitoring/      # Collecteur métriques, health checks, RerunProfiler
├── observability/   # Contexte d'observabilité (spans, traces)
├── resilience/      # Politiques de résilience composables (retry, timeout, bulkhead)
├── result/          # Result Monad (Ok/Err) — gestion d'erreurs style Rust
├── state/           # Package: manager.py, shortcuts.py, slices.py
├── validation/      # Schemas Pydantic (7 domaines), sanitizer
├── async_utils.py   # Utilitaires asynchrones
├── bootstrap.py     # demarrer_application() — initialisation IoC
├── constants.py     # Constantes globales
├── container.py     # IoC Container — injection de dépendances typée
├── errors.py        # Classes d'erreurs métier (UI)
├── exceptions.py   # Classe de base ExceptionApp + guards (→ sera renommé exceptions.py)
├── lazy_loader.py   # ChargeurModuleDiffere (chargement différé des modules)
├── logging.py       # Configuration logging
├── repository.py    # Repository générique CRUD typé
├── session_keys.py  # Clés de session typées (KeyNamespace)
├── specifications.py # Specification Pattern — critères composables
├── storage.py       # SessionStorage Protocol (découplage Streamlit)
├── unit_of_work.py  # Transaction atomique avec rollback automatique
└── py.typed         # Marqueur PEP 561 pour typing
```

### config/ — Configuration centralisée

```python
# Pydantic BaseSettings avec chargement en cascade:
# .env.local → .env → st.secrets → constantes
from src.core.config import obtenir_parametres
config = obtenir_parametres()
```

Fichiers: `settings.py` (Parametres), `loader.py` (chargement .env, secrets Streamlit), `validator.py` (ValidateurConfiguration)

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

### state/ — État applicatif (package)

```python
from src.core.state import GestionnaireEtat, obtenir_etat, naviguer, revenir
from src.core.state import EtatNavigation, EtatCuisine, EtatUI

etat = obtenir_etat()
etat.navigation.module_actuel  # "cuisine.recettes"
etat.cuisine.id_recette_visualisation  # 42
```

Fichiers: `manager.py` (GestionnaireEtat), `shortcuts.py` (naviguer, revenir), `slices.py` (EtatNavigation, EtatCuisine, EtatUI)

### result/ — Result Monad

```python
from src.core.result import Ok, Err, Result, failure, ErrorCode

def charger_recette(id: int) -> Result[Recette, ErrorInfo]:
    recette = db.get(id)
    if not recette:
        return failure(ErrorCode.NOT_FOUND, f"Recette #{id} introuvable")
    return Ok(recette)
```

Fichiers: `base.py` (Ok, Err, Result), `codes.py` (ErrorCode), `combinators.py`, `decorators.py` (@result_api), `helpers.py`

### resilience/ — Politiques de résilience

```python
from src.core.resilience import RetryPolicy, TimeoutPolicy, politique_ia

politique = RetryPolicy(3) + TimeoutPolicy(30)
result = politique.executer(lambda: appel_risque())
```

### middleware/ — Pipeline composable

```python
from src.core.middleware import Pipeline

pipeline = Pipeline().utiliser(LogMiddleware()).utiliser(RetryMiddleware(max_retries=3))
result = pipeline.executer(lambda ctx: operation(ctx))
```

Fichiers: `base.py`, `builtin.py` (middlewares built-in), `pipeline.py`

### monitoring/ — Métriques & Performance

```python
from src.core.monitoring import RerunProfiler, CollecteurMetriques

# Profilage des reruns Streamlit
profiler = RerunProfiler()
```

Fichiers: `collector.py`, `decorators.py`, `health.py`, `rerun_profiler.py`

### bootstrap.py — Initialisation

```python
from src.core.bootstrap import demarrer_application

# Appelé au démarrage dans src/app.py — initialise l'IoC container
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

### repository.py — Repository générique

```python
from src.core.repository import Repository
from src.core.models import Recette

repo = Repository(Recette, session)
recettes = repo.lister(filtres={"categorie": "dessert"}, limite=10)
recette = repo.creer({"nom": "Tarte", "categorie": "dessert"})
```

### storage.py — Abstraction SessionStorage

```python
from src.core.storage import obtenir_storage, MemorySessionStorage

# Production: StreamlitSessionStorage (st.session_state)
# Tests/CLI: MemorySessionStorage (dict)
storage = obtenir_storage()
storage["clé"] = valeur
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
│   ├── cqrs/           # Commands, Queries, Dispatcher (CQRS pattern)
│   ├── events/         # Bus d'événements (bus.py, events.py, subscribers.py)
│   ├── middleware/      # Middlewares service-level
│   ├── notifications/  # Web push, NTFY, templates, persistance
│   ├── observability/  # Health checks, métriques, spans
│   ├── specifications/ # Specs domaine (inventaire.py, recettes.py)
│   ├── utilisateur/    # Préférences, historique
│   └── registry.py     # Registre de services
├── cuisine/            # Recettes, courses, planning repas
├── famille/            # Services famille
├── integrations/       # APIs externes (codes-barres, factures, Garmin, météo, images)
├── inventaire/         # Gestion des stocks
├── jeux/               # Loto, paris sportifs
├── maison/             # Entretien, dépenses, jardin, projets
└── rapports/           # Export PDF, rapports budget/gaspillage
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

## Lazy Loading (st.navigation + ChargeurModuleDiffere)

Le routage multi-pages utilise `st.navigation()` configuré dans `src/core/navigation.py` via `construire_pages()`.
Le chargement différé des modules est géré par `ChargeurModuleDiffere` dans `src/core/lazy_loader.py`.

```python
# src/core/navigation.py — construire_pages() enregistre chaque module comme st.Page()
# Chaque module exporte app() comme point d'entrée
def app():
    """Point d'entrée module"""
    st.title("Mon Module")
```

**Performance**: ~60% d'accélération au démarrage grâce au chargement différé

**Bootstrap**: `src/app.py` appelle `demarrer_application()` (IoC) puis `st.navigation()` charge le module sélectionné.

## Modules Métier (src/modules/)

Chaque module est un sous-package avec `__init__.py` exportant `app()`:

| Module         | Sous-modules                                                                                                                 | Description                               |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| `_framework/`  | `base_module.py`, `error_boundary.py`, `fragments.py`, `state_manager.py`                                                    | Framework de base pour modules            |
| `accueil/`     | `dashboard.py`                                                                                                               | Tableau de bord, métriques, alertes       |
| `cuisine/`     | `recettes/`, `courses/`, `inventaire/`, `planificateur_repas/`, `batch_cooking_detaille.py`                                  | Recettes, courses, stocks, planning repas |
| `famille/`     | `activites.py`, `routines.py`, `jules/`, `jules_planning.py`, `suivi_perso/`, `achats_famille/`, `weekend/`, `hub_famille.py`, `age_utils.py` | Vie familiale, suivi enfant, santé        |
| `maison/`      | `entretien/`, `charges/`, `depenses/`, `jardin/`, `hub/`                                                                     | Habitat, entretien, dépenses              |
| `jeux/`        | `loto/`, `paris/`, `scraper_loto.py`, `utils.py`                                                                             | Loto, paris sportifs                      |
| `planning/`    | `calendrier/`, `components/`, `timeline_ui.py`, `templates_ui.py`                                                            | Calendrier, timeline                      |
| `parametres/`  | `about.py`, `affichage.py`, `budget.py`, `cache.py`, `database.py`, `foyer.py`, `ia.py`, `utils.py`                          | Réglages applicatifs                      |
| `utilitaires/` | `barcode/`, `barcode_utils.py`, `rapports.py`, `rapports_utils.py`, `notifications_push.py`, `scan_factures.py`, `recherche_produits.py` | Outils transversaux                       |

## Composants UI (src/ui/)

```
src/ui/
├── components/      # Widgets réutilisables (alertes, atoms, charts, data, filters, forms,
│                    #   layouts, metrics, metrics_row, streaming, system, dynamic)
├── dialogs.py       # DialogBuilder — modales fluides
├── engine/          # Moteur CSS
├── feedback/        # smart_spinner, show_success, show_error, show_warning
├── forms/           # FormBuilder — formulaires déclaratifs (builder, fields, rendering, types)
├── fragments.py     # @ui_fragment, @auto_refresh, FragmentGroup
├── integrations/    # google_calendar.py
├── keys.py          # Clés UI typées
├── layout/          # Header, footer, sidebar, styles, initialisation
├── layouts/         # Row, Grid, Stack composables
├── registry.py      # Registre de composants
├── state/           # URL State — deep linking (url.py)
├── system/          # Composants système
├── tablet/          # UI tablette (config, kitchen, styles, timer, widgets)
├── testing/         # Régression visuelle
├── theme.py         # Thème et tokens
├── tokens.py        # Design tokens primitifs
├── tokens_semantic.py # Design tokens sémantiques
├── views/           # Vues spécifiques (auth, historique, import, jeux, météo,
│                    #   notifications, PWA, sauvegarde, synchronisation)
├── a11y.py          # Accessibilité
├── animations.py    # Animations UI
└── utils.py         # Utilitaires UI
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
