# Instructions Copilot pour Codebase Assistant Matanne

## Vue d'ensemble du projet

**Type**: Application Streamlit de gestion familiale  
**Langage**: Python 3.13+ avec SQLAlchemy 2.0 ORM  
**Base de données**: Supabase PostgreSQL avec migrations SQL-file  
**Stack clé**: Streamlit, SQLAlchemy, Pydantic v2, API Mistral AI, pandas, Plotly

Hub de gestion familiale en production avec modules pour:

- 🍽️ Recettes et planification des repas (suggestions IA)
- 🛍️ Listes de courses et scans de codes-barres
- 📅 Planification d'activités et routines familiales
- 👶 Suivi du développement de l'enfant (Jules, 19m)
- 💪 Suivi de la santé et du fitness
- 📊 Tableau de bord familial avec métriques

**Architecture**: Chargement différé avec ~60% d'accélération au démarrage via `ChargeurModuleDiffere` et `st.navigation()`, modèles SQLAlchemy modulaires dans `core/models/` (22 fichiers), codebase en français. Marqueur `py.typed` (PEP 561).

---

## Architecture

### Modules principaux (src/core/)

Le core est organisé en **11 sous-packages** + fichiers utilitaires.

- **ai/**: `ClientIA` (client Mistral), `AnalyseurIA` (parsing JSON/Pydantic), `CacheIA` (cache sémantique), `RateLimitIA` (rate limiting), `CircuitBreaker` (résilience API)
- **caching/**: Cache multi-niveaux — `base.py` (types), `memory.py` (L1), `session.py` (L2), `file.py` (L3), `orchestrator.py` (CacheMultiNiveau, obtenir_cache). Décorateur unifié `@avec_cache`
- **config/**: Pydantic `BaseSettings` — `settings.py` (Parametres, obtenir_parametres), `loader.py` (chargement .env, secrets Streamlit), `validator.py` (ValidateurConfiguration)
- **date_utils/**: Package utilitaires de dates — `semaines.py`, `periodes.py`, `formatage.py`, `helpers.py`. Re-exports transparents via `__init__.py`.
- **db/**: Base de données — `engine.py` (Engine SQLAlchemy, QueuePool), `session.py` (context managers), `migrations.py` (GestionnaireMigrations SQL-file), `utils.py` (health checks)
- **decorators/**: Package décorateurs — `db.py` (`@avec_session_db`), `cache.py` (`@avec_cache`), `errors.py` (`@avec_gestion_erreurs`), `validation.py` (`@avec_validation`, `@avec_resilience`)
- **models/**: Modèles SQLAlchemy ORM modulaires (22 fichiers organisés par domaine)
- **monitoring/**: Métriques & performance — `collector.py`, `decorators.py`, `health.py`, `rerun_profiler.py`
- **observability/**: Contexte d'observabilité — `context.py`
- **resilience/**: Politiques de résilience composables — `policies.py`. `executer()` retourne `T` directement ou lève une exception.
- **state/**: Package état applicatif — `manager.py` (GestionnaireEtat), `shortcuts.py` (naviguer, revenir), `slices.py` (EtatNavigation, EtatCuisine, EtatUI)
- **validation/**: Package validation — `schemas/` (sous-package Pydantic: `recettes.py`, `inventaire.py`, `courses.py`, `planning.py`, `famille.py`, `projets.py`, `_helpers.py`), `sanitizer.py` (anti-XSS/injection), `validators.py` (helpers)
- **Utilitaires**: `bootstrap.py` (init config + events), `constants.py`, `exceptions.py` (exceptions pures sans UI), `lazy_loader.py` (ChargeurModuleDiffere), `logging.py`, `navigation.py` (construire_pages, st.navigation), `session_keys.py` (KeyNamespace), `storage.py` (SessionStorage Protocol), `async_utils.py`, `py.typed`

### Couche Services (src/services/)

- **core/base/**: `BaseAIService` (dans `ai_service.py`) avec limitation de débit intégrée, cache sémantique, parsing JSON, mixins IA, streaming, protocols, pipeline
- **core/registry.py**: Registre de services avec décorateur `@service_factory` pour singletons
- **core/events/**: Bus d'événements pub/sub avec wildcards
- **famille/**: Services IA famille — `jules_ai.py` (JulesAIService), `weekend_ai.py` (WeekendAIService)
- **recettes/**: Service recettes avec `importer.py` pour import URL/PDF
- **planning/**: Service modulaire divisé en sous-modules:
  - `nutrition.py`: Équilibre nutritionnel
  - `agregation.py`: Agrégation des courses
  - `formatters.py`: Formatage pour l'UI
  - `validators.py`: Validation des plannings
  - `prompts.py`: Génération de prompts IA
- **courses.py**, **inventaire.py**: Services spécifiques au domaine
- **barcode.py**, **rapports_pdf.py**, **predictions.py**: Services utilitaires
- Tous exportent des fonctions factory `get_{service_name}_service()` décorées avec `@service_factory` pour le singleton via registre

### Composants UI (src/ui/)

- **components/**: Widgets Streamlit réutilisables (boutons, cartes, tableaux, modales, badges)
- **feedback/**: Utilitaires `smart_spinner()`, `show_success()`, `show_error()`, `show_warning()`
- **core/**: Constructeurs de formulaires, gestionnaires de modales avec décorateurs `@st.cache_data`
- **layout/**: Header, footer, sidebar, styles
- Tous les composants retournent des objets Streamlit directement (pas de wrappers)

### Modules Métier (src/modules/)

Chaque module exporte la fonction `app()` (point d'entrée pour le chargement différé):

- **accueil/**: Tableau de bord avec métriques familiales, alertes critiques, raccourcis rapides
- **cuisine/**: Recettes, planification des repas, gestion des stocks, cours, inventaire, batch cooking
- **famille/**: Hub de la vie familiale: suivi de Jules (enfant), activités, routines, achats, suivi_perso, weekend. Inclut `activites_utils.py` et `routines_utils.py` (logique pure testable)
- **maison/**: Habitat, entretien, charges, dépenses, jardin
- **jeux/**: Loto et paris sportifs
- **planning/**: Calendrier, timeline, templates
- **parametres/**: Paramètres multi-onglets (about, affichage, budget, cache, database, foyer, ia)
- **utilitaires/**: Barcode, rapports, notifications push, scan factures, recherche produits

---

## Flux de travail critiques pour les développeurs

### Lancer l'application

```bash
# Développement (point d'entrée principal)
streamlit run src/app.py

# Mode débogage avec logging détaillé
streamlit run --logger.level=debug src/app.py

# Via l'assistant manage.py
python manage.py run
```

### Base de données

```bash
# Initialisation complète du schéma (94 tables, RLS, triggers, vues)
# Exécuter sql/INIT_COMPLET.sql dans Supabase SQL Editor ou psql

# Vérifier la connexion
python -c "from src.core.db import obtenir_moteur; obtenir_moteur().connect()"
```

### Tests

```bash
# Tous les tests avec rapport de couverture (HTML + terminal)
python manage.py test_coverage
# Exécute: pytest --cov=src --cov-report=html --cov-report=term-missing

# Fichier de test spécifique
pytest tests/test_famille.py -v

# Test unique
pytest tests/test_famille.py::TestFamille::test_method -v

# Seulement les tests d'intégration
pytest -m integration
```

### Qualité du code

```bash
# Formate le code (ruff format, longueur de ligne 100)
python manage.py format_code

# Vérifie le code (ruff)
python manage.py lint

# Génère requirements.txt depuis pyproject.toml
python manage.py generate_requirements
```

---

## Conventions spécifiques au projet

### Nommage et langage

- **Français partout**: Tous les noms de variables, commentaires, docstrings et noms de fonctions utilisent le français (ex: `obtenir_parametres()`, `GestionnaireMigrations`, `avec_session_db`)
- **Structure des fichiers**: Modèles SQLAlchemy dans `src/core/models/` (22 fichiers modulaires), tous les décorateurs dans `src/core/decorators/`, utilitaires dans `src/core/` (date_utils/, constants, exceptions, errors, state)
- **Nommage des modules**: Les modules sont `src/modules/{name}.py` ou `src/modules/{name}/__init__.py`
- **Factories de services**: Toujours exporter une fonction `get_{service_name}_service()` décorée avec `@service_factory` pour le singleton via registre (ex: `get_recette_service()`)

### Points d'entrée

- **Modules Streamlit**: Chaque module DOIT exporter une fonction `app()` comme point d'entrée:
  ```python
  def app():
      """Point d'entrée module"""
      # Logique du module ici
  ```
- **Chargement différé**: `st.navigation()` via `navigation.py` charge `module.app()` quand l'utilisateur sélectionne le module
- Pas de renommage de fonctions (ne pas utiliser `afficher()` ou autres - s'en tenir à `app()`)

### Modèle de gestion des erreurs

```python
# Backend/services (pas de dépendance UI)
from src.core.exceptions import ErreurBaseDeDonnees

# Modules Streamlit (avec helpers d'affichage UI)
from src.ui.feedback import afficher_erreur
from src.core.exceptions import ErreurBaseDeDonnees

try:
    result = perform_operation()
except Exception as e:
    logger.error(f"L'opération a échoué: {e}")
    raise ErreurBaseDeDonnees("Message convivial pour l'utilisateur")
```

Voir [src/core/exceptions.py](src/core/exceptions.py) (exceptions pures), [src/ui/feedback/](src/ui/feedback/) (helpers UI afficher_erreur/succes) et [src/core/decorators/](src/core/decorators/) pour le décorateur `@avec_gestion_erreurs`.

### Gestion des sessions de base de données

```python
from src.core.db import obtenir_contexte_db
from src.core.decorators import avec_session_db

# Modèle 1: Utiliser le décorateur (préféré pour les fonctions pures)
@avec_session_db
def create_recipe(data: dict, db: Session) -> Recette:
    recette = Recette(**data)
    db.add(recette)
    db.commit()
    return recette

# Modèle 2: Gestionnaire de contexte manuel (pour les flux complexes)
with obtenir_contexte_db() as session:
    result = session.query(Recette).first()
    session.commit()
```

Clé: Toujours utiliser `obtenir_contexte_db()` — ne jamais créer Engine/Session directement.

### Stratégie de cache

- **Cache multi-niveaux unifié**: `@avec_cache(ttl=300)` dans `src/core/decorators/cache.py` — délègue à `CacheMultiNiveau` (L1 mémoire → L2 session → L3 fichier)
- **Cache Streamlit**: `@st.cache_data` uniquement pour les composants retournant des objets Streamlit/Plotly
- **Cache des réponses IA**: `CacheIA` dans `src/core/ai/cache.py` pour le cache sémantique des appels IA
- **Invalidation manuelle**: `Cache.invalider(pattern="prefix_")` ou `cache.invalider_par_tag("tag")`
- Exemple:

  ```python
  from src.core.decorators import avec_cache

  @avec_cache(ttl=300)
  def get_recettes(): ...
  ```

> **Règle**: Utiliser `@avec_cache` dans les services/métier. Réserver `@st.cache_data` aux composants UI retournant des objets Streamlit.

### Modèle de chargement différé

Les modules sont chargés à la demande seulement quand ils sont sélectionnés:

```python
# Dans app.py: géré automatiquement via st.navigation() + construire_pages()
# Chaque module est enregistré comme st.Page() dans src/core/navigation.py
# La fonction app() est appelée automatiquement par Streamlit
```

Garder les imports de modules DANS la fonction `app()`, pas au niveau du module, pour préserver la performance du démarrage.

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

### Navigation

Toujours utiliser `naviguer()` — ne jamais modifier `st.session_state` directement:

```python
from src.core.state import naviguer
naviguer("cuisine.recettes")  # Gère rerun automatiquement
```

---

## Points d'intégration et dépendances

### APIs externes

- **Mistral AI**: Client à `src/core/ai/client.py`, configuré dans [src/core/config/](src/core/config/). Tous les appels IA passent par `BaseAIService` avec limitation de débit et cache intégrés.
- **Supabase PostgreSQL**: Connexion via `DATABASE_URL` depuis `.env.local`. Format: `postgresql://user:password@host/db`
- **Limites de débit**: `AI_RATE_LIMIT_DAILY`, `AI_RATE_LIMIT_HOURLY` définis dans [src/core/constants.py](src/core/constants.py)

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

Clé: Tous les appels IA sont enveloppés avec limitation de débit automatique, cache sémantique et récupération d'erreurs.

### Communication inter-modules

- **Helpers partagés**: `src/modules/famille/helpers.py` et modules de logique pure (`activites_utils.py`, `routines_utils.py`) avec constantes, filtrage, statistiques, recommandations
- **Gestion d'état**: `GestionnaireEtat` dans [src/core/state/](src/core/state/) fournit un magasin clé-valeur global (nom de famille, préférences utilisateur)
- **Relations de base de données**: SQLAlchemy `relationship()` avec `back_populates` pour l'accès aux objets bidirectionnel entre modèles

### Sources de configuration (en cascade)

1. Fichier `.env.local` (racine du projet, plus haute priorité)
2. Fichier `.env` (fallback)
3. Secrets du cloud Streamlit (`st.secrets`)
4. Valeurs par défaut codées en dur dans [src/core/constants.py](src/core/constants.py)

Importer via: `from src.core.config import obtenir_parametres()`

---

## Modèles courants à suivre

### Ajouter un nouveau module

1. Créer `src/modules/mymodule.py` ou `src/modules/mymodule/__init__.py`
2. Exporter la fonction `app()` comme point d'entrée:
   ```python
   def app():
       """Point d'entrée module mymodule"""
       st.title("Mon Module")
       # Logique du module ici
   ```
3. Utiliser les composants UI chargés paresseusement depuis `src.ui`
4. Interroger la base de données via les fonctions décorées avec `@avec_session_db`
5. Ajouter une page dans `construire_pages()` dans [src/core/navigation.py](src/core/navigation.py)

### Ajouter un modèle de base de données

1. Ajouter la classe dans le fichier approprié sous [src/core/models/](src/core/models/) en héritant de `Base`
2. Suivre les modèles ORM SQLAlchemy 2.0 avec indices de type `mapped_column` et `Mapped`
3. Utiliser la convention de nommage pour les contraintes (déjà configurée dans models.py)
4. Ajouter le CREATE TABLE dans `sql/INIT_COMPLET.sql` (section appropriée)
5. Ajouter RLS et triggers dans les sections correspondantes

### Intégration IA

```python
from src.services.core.base import BaseAIService
from src.core.ai import ClientIA

class RecipeService(BaseAIService):
    """Service avec intégration IA automatique"""

    def generate_shopping_list(self, recipes: list[Recette]) -> list[dict]:
        """Générer la liste à partir des recettes avec IA et limitation de débit automatique"""
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
# Dans tests/test_mymodule.py
import pytest
from sqlalchemy.orm import Session

@pytest.mark.unit
def test_create_recipe(test_db: Session):
    """Tester l'opération de base de données avec fixture"""
    from src.services.recettes import RecetteService

    service = RecetteService(test_db)
    result = service.creer_recette({"nom": "Tarte"})

    assert result.nom == "Tarte"
    # Session nettoyée automatiquement après le test
```

Clé: `conftest.py` fournit des fixtures de base de données SQLite en mémoire pour des tests isolés.

---

## Référence des fichiers clés

| Fichier                                                            | Objectif                                                      |
| ------------------------------------------------------------------ | ------------------------------------------------------------- |
| [src/core/config/](src/core/config/)                               | Package configuration (Pydantic BaseSettings)                 |
| [src/core/db/](src/core/db/)                                       | Package base de données (engine, sessions, migrations)        |
| [src/core/caching/](src/core/caching/)                             | Package cache multi-niveaux (L1/L2/L3, @avec_cache unifié)    |
| [src/core/date_utils/](src/core/date_utils/)                       | Package utilitaires dates (semaines, periodes, formatage)     |
| [src/core/validation/](src/core/validation/)                       | Package validation (schemas/ sous-package, sanitizer)         |
| [src/core/monitoring/](src/core/monitoring/)                       | Package métriques & performance                               |
| [src/core/ai/](src/core/ai/)                                       | Package IA (Mistral, rate limiting, cache, circuit breaker)   |
| [src/core/models/](src/core/models/)                               | Tous les modèles ORM SQLAlchemy (22 fichiers)                 |
| [src/core/decorators/](src/core/decorators/)                       | Package décorateurs (`@avec_session_db`, `@avec_cache`, etc.) |
| [src/core/state/](src/core/state/)                                 | Package état applicatif (manager, slices, shortcuts)          |
| [src/core/resilience/](src/core/resilience/)                       | Politiques de résilience composables (retourne T directement) |
| [src/core/storage.py](src/core/storage.py)                         | SessionStorage Protocol (découplage Streamlit)                |
| [src/services/core/registry.py](src/services/core/registry.py)     | Registre de services + @service_factory                       |
| [src/services/core/events/](src/services/core/events/)             | Bus d'événements pub/sub avec wildcards                       |
| [src/services/core/base/](src/services/core/base/)                 | BaseAIService, mixins IA, streaming, protocols                |
| [src/app.py](src/app.py)                                           | App Streamlit principale, bootstrap, chargement différé       |
| [src/core/navigation.py](src/core/navigation.py)                   | Routage multi-pages (construire_pages, st.navigation)         |
| [pyproject.toml](pyproject.toml)                                   | Dépendances (Poetry), config test, règles de linting          |
| [docs/MIGRATION_CORE_PACKAGES.md](docs/MIGRATION_CORE_PACKAGES.md) | Guide de migration des imports                                |

---

## Débogage rapide

**Module ne se charge pas?**

- Vérifier que la fonction `app()` existe
- Vérifier la page dans `construire_pages()` dans [src/core/navigation.py](src/core/navigation.py)

**Connexion à la base de données échouée?**

- Vérifier `DATABASE_URL` dans `.env.local`: format `postgresql://user:pass@host/db`
- Exécuter: `python -c "from src.core.db import obtenir_moteur; obtenir_moteur().connect()"`

**Tests échouent?**

- Conftest.py fournit des fixtures de BD SQLite en mémoire pour les tests isolés
- Utiliser `pytest tests/test_name.py::TestClass::test_method -v` pour un test unique
- Après refactoring de tests, toujours supprimer `__pycache__/` (tests/ + src/) pour éviter les `.pyc` obsolètes

**Les migrations ne s'appliquent pas?**

- Vérifier `sql/migrations/` pour les erreurs de syntaxe SQL
- Vérifier la table `schema_migrations` dans la base de données
- Exécuter `python manage.py migrate` pour voir les détails
