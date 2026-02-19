# Instructions Copilot pour Codebase Assistant Matanne

## Vue d'ensemble du projet

**Type**: Application Streamlit de gestion familiale  
**Langage**: Python 3.11+ avec SQLAlchemy 2.0 ORM  
**Base de données**: Supabase PostgreSQL avec migrations Alembic  
**Stack clé**: Streamlit, SQLAlchemy, Pydantic v2, API Mistral AI, pandas, Plotly

Hub de gestion familiale en production avec modules pour:

- 🍽️ Recettes et planification des repas (suggestions IA)
- 🛍️ Listes de courses et scans de codes-barres
- 📅 Planification d'activités et routines familiales
- 👶 Suivi du développement de l'enfant (Jules, 19m)
- 💪 Suivi de la santé et du fitness
- 📊 Tableau de bord familial avec métriques

**Architecture**: Chargement différé avec ~60% d'accélération au démarrage via `OptimizedRouter`, modèles SQLAlchemy modulaires dans `core/models/` (18 fichiers), codebase en français.

---

## Architecture

### Modules principaux (src/core/)

Le core est organisé en **4 sous-packages** + fichiers utilitaires.

- **config/**: Package Pydantic `BaseSettings` — `settings.py` (Parametres, obtenir_parametres), `loader.py` (chargement .env, secrets Streamlit)
- **db/**: Package base de données — `engine.py` (Engine SQLAlchemy, QueuePool), `session.py` (context managers), `migrations.py` (GestionnaireMigrations), `utils.py` (health checks)
- **caching/**: Package cache multi-niveaux — `memory.py` (L1 dict), `session.py` (L2 session_state), `file.py` (L3 pickle), `orchestrator.py` (CacheMultiNiveau, @avec_cache_multi)
- **validation/**: Package validation — `schemas.py` (modèles Pydantic), `sanitizer.py` (anti-XSS/injection), `validators.py` (helpers)
- **models/**: Modèles SQLAlchemy ORM modulaires (19 fichiers organisés par domaine)
- **ai/**: Sous-module avec `ClientIA` (client Mistral), `AnalyseurIA` (parsing JSON/Pydantic), `CacheIA` (cache sémantique), `RateLimitIA` (source de vérité rate limiting)
- **decorators.py**: `@with_db_session`, `@with_cache`, `@with_error_handling`
- **Utilitaires**: `date_utils.py`, `formatters/`, `helpers/`, `constants.py`, `errors.py`

### Couche Services (src/services/)

- **base/**: `BaseAIService` avec limitation de débit intégrée, cache sémantique, parsing JSON, gestion d'erreurs unifiée
- **recettes/**: Service recettes avec `importer.py` pour import URL/PDF
- **planning/**: Service modulaire divisé en sous-modules:
  - `nutrition.py`: Équilibre nutritionnel
  - `agregation.py`: Agrégation des courses
  - `formatters.py`: Formatage pour l'UI
  - `validators.py`: Validation des plannings
  - `prompts.py`: Génération de prompts IA
- **courses.py**, **inventaire.py**: Services spécifiques au domaine
- **barcode.py**, **rapports_pdf.py**, **predictions.py**: Services utilitaires
- Tous exportent des fonctions factory `get_{service_name}_service()` pour l'injection de dépendances

### Composants UI (src/ui/)

- **components/**: Widgets Streamlit réutilisables (boutons, cartes, tableaux, modales, badges)
- **feedback/**: Utilitaires `smart_spinner()`, `show_success()`, `show_error()`, `show_warning()`
- **core/**: Constructeurs de formulaires, gestionnaires de modales avec décorateurs `@st.cache_data`
- **layout/**: Header, footer, sidebar, styles
- Tous les composants retournent des objets Streamlit directement (pas de wrappers)

### Modules Métier (src/modules/)

Chaque module exporte la fonction `app()` (point d'entrée pour le chargement différé):

- **accueil.py**: Tableau de bord avec métriques familiales, alertes critiques, raccourcis rapides
- **cuisine/**: Recettes, planification des repas, gestion des stocks
- **famille/**: Hub de la vie familiale: suivi de Jules (enfant), santé/bien-être, activités, achats
- **planning/**: Calendrier, routines, planification d'activités
- **barcode.py**: Scan de codes-barres pour les courses/stocks
- **parametres.py**: Paramètres, vérification de la santé de la base de données, runner de migrations

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

### Base de données et migrations

```bash
# Génère automatiquement une migration à partir des changements de modèles
python manage.py create_migration
# Vous demande un message, exécute: alembic revision --autogenerate -m "message"

# Applique les migrations en attente
python manage.py migrate
# Exécute: alembic upgrade head

# Vérifie la version actuelle de migration
python -c "from src.core.database import GestionnaireMigrations; print(GestionnaireMigrations.obtenir_version_courante())"

# Voir le statut d'Alembic
alembic current
alembic history
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
# Formate le code (black, longueur de ligne 100)
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
- **Structure des fichiers**: Modèles SQLAlchemy dans `src/core/models/` (18 fichiers modulaires), tous les décorateurs dans `src/core/decorators.py`, utilitaires dans `src/core/` (date_utils, formatters, helpers)
- **Nommage des modules**: Les modules sont `src/modules/{name}.py` ou `src/modules/{name}/__init__.py`
- **Factories de services**: Toujours exporter une fonction `get_{service_name}_service()` pour l'injection de dépendances (ex: `get_recette_service()`)

### Points d'entrée

- **Modules Streamlit**: Chaque module DOIT exporter une fonction `app()` comme point d'entrée:
  ```python
  def app():
      """Point d'entrée module"""
      # Logique du module ici
  ```
- **Chargement différé**: `OptimizedRouter` appelle `module.app()` quand l'utilisateur sélectionne le module
- Pas de renommage de fonctions (ne pas utiliser `afficher()` ou autres - s'en tenir à `app()`)

### Modèle de gestion des erreurs

```python
from src.core.errors import ErreurBaseDeDonnees

try:
    result = perform_operation()
except Exception as e:
    logger.error(f"L'opération a échoué: {e}")
    raise ErreurBaseDeDonnees("Message convivial pour l'utilisateur")
```

Voir [src/core/errors.py](src/core/errors.py) et [src/core/decorators.py](src/core/decorators.py#L1) pour le décorateur `@gerer_erreurs`.

### Gestion des sessions de base de données

```python
from src.core.db import obtenir_contexte_db
from src.core.decorators import with_db_session

# Modèle 1: Utiliser le décorateur (préféré pour les fonctions pures)
@with_db_session
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

- **Cache multi-niveaux**: `src/core/caching/` — L1 mémoire, L2 session, L3 fichier avec `@avec_cache_multi`
- **Cache Streamlit**: `@st.cache_data(ttl=1800)` pour les données UI (par défaut 30 min)
- **Cache des réponses IA**: `CacheIA` dans `src/core/ai/cache.py` pour le cache sémantique des appels IA
- **Invalidation manuelle**: `StateManager` peut nettoyer le cache lors d'actions utilisateur
- Exemple:
  ```python
  from src.core.caching import obtenir_cache
  cache = obtenir_cache()
  # Utilisation via orchestrateur multi-niveaux
  ```

### Modèle de chargement différé

Les modules sont chargés à la demande seulement quand ils sont sélectionnés:

```python
# Dans app.py: géré automatiquement via OptimizedRouter
if hasattr(module, "app"):
    module.app()  # Point d'entrée du module chargé différemment
```

Garder les imports de modules DANS la fonction `app()`, pas au niveau du module, pour préserver la performance du démarrage.

---

## Points d'intégration et dépendances

### APIs externes

- **Mistral AI**: Client à `src/core/ai/client.py`, configuré dans [config.py](src/core/config.py). Tous les appels IA passent par `BaseAIService` avec limitation de débit et cache intégrés.
- **Supabase PostgreSQL**: Connexion via `DATABASE_URL` depuis `.env.local`. Format: `postgresql://user:password@host/db`
- **Limites de débit**: `AI_RATE_LIMIT_DAILY`, `AI_RATE_LIMIT_HOURLY` définis dans [src/core/constants.py](src/core/constants.py)

### Intégration du service IA

```python
from src.services.base_ai_service import BaseAIService
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

- **Helpers partagés**: `src/modules/famille/helpers.py` fournit des fonctions réutilisables avec décorateurs `@st.cache_data`
- **Gestion d'état**: `StateManager` dans [src/core/state.py](src/core/state.py) fournit un magasin clé-valeur global (nom de famille, préférences utilisateur)
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
4. Interroger la base de données via les fonctions décorées avec `@with_db_session`
5. Enregistrer dans `OptimizedRouter.MODULE_REGISTRY` dans [src/app.py](src/app.py) (auto-découverte si suit la convention de nommage)

### Ajouter un modèle de base de données

1. Ajouter la classe dans le fichier approprié sous [src/core/models/](src/core/models/) en héritant de `Base`
2. Suivre les modèles ORM SQLAlchemy 2.0 avec indices de type `mapped_column` et `Mapped`
3. Utiliser la convention de nommage pour les contraintes (déjà configurée dans models.py)
4. Créer la migration: `python manage.py create_migration "Add new model fields"`
5. Migration générée automatiquement par la fonctionnalité autogenerate d'Alembic
6. Les fichiers de migration apparaissent dans `alembic/versions/` numérotés avec préfixe de date

### Intégration IA

```python
from src.services.base_ai_service import BaseAIService
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

| Fichier                                          | Objectif                                              |
| ------------------------------------------------ | ----------------------------------------------------- |
| [src/core/config/](src/core/config/)             | Package configuration (Pydantic BaseSettings)         |
| [src/core/db/](src/core/db/)                     | Package base de données (engine, sessions, migrations)|
| [src/core/caching/](src/core/caching/)           | Package cache multi-niveaux (L1/L2/L3)                |
| [src/core/validation/](src/core/validation/)     | Package validation & sanitization                     |
| [src/core/monitoring/](src/core/monitoring/)      | Package métriques & performance                       |
| [src/core/ai/](src/core/ai/)                     | Package IA (Mistral, rate limiting, cache sémantique) |
| [src/core/models/](src/core/models/)             | Tous les modèles ORM SQLAlchemy (18 fichiers)         |
| [src/core/decorators.py](src/core/decorators.py) | Utilitaires `@with_db_session`, `@with_cache`         |
| [src/app.py](src/app.py)                         | App Streamlit principale, routage, chargement différé |
| [pyproject.toml](pyproject.toml)                 | Dépendances (Poetry), config test, règles de linting  |
| [alembic/env.py](alembic/env.py)                 | Configuration d'environnement des migrations          |
| [docs/MIGRATION_CORE_PACKAGES.md](docs/MIGRATION_CORE_PACKAGES.md) | Guide de migration des imports    |

---

## Débogage rapide

**Module ne se charge pas?**

- Vérifier que la fonction `app()` existe
- Vérifier le chemin du chargeur paresseux dans `MODULE_REGISTRY`

**Connexion à la base de données échouée?**

- Vérifier `DATABASE_URL` dans `.env.local`: format `postgresql://user:pass@host/db`
- Exécuter: `python -c "from src.core.db import obtenir_moteur; obtenir_moteur().connect()"`

**Tests échouent?**

- Conftest.py fournit des fixtures de BD SQLite en mémoire pour les tests isolés
- Utiliser `pytest tests/test_name.py::TestClass::test_method -v` pour un test unique

**Les migrations ne s'appliquent pas?**

- Vérifier `alembic/versions/` pour les erreurs de syntaxe
- Assurer que tous les imports dans les fichiers de migration sont valides
- Exécuter `alembic current` pour voir la version appliquée
