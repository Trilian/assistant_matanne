# 🧪 Structure des Tests - Assistant Matanne

## Organisation des dossiers

```
tests/
├── conftest.py              # Fixtures partagées (DB, factories, mocks)
├── test_app_main.py         # Tests du point d'entrée principal
│
├── api/                     # Tests des endpoints FastAPI
│   ├── conftest.py          # Fixtures API (client, auth)
│   ├── test_api_endpoints_basic.py    # GET endpoints
│   ├── test_api_endpoints_crud.py     # PUT, DELETE, PATCH
│   └── test_api_integration.py        # Tests d'intégration multi-endpoints
│
├── core/                    # Tests du noyau applicatif
│   ├── test_config.py       # Configuration et settings
│   ├── test_database.py     # Connexion et sessions DB
│   ├── test_decorators.py   # @with_db_session, @with_cache
│   ├── test_errors.py       # Gestion des erreurs
│   ├── test_cache.py        # Système de cache
│   ├── test_state.py        # Gestion de l'état
│   ├── test_lazy_loader.py  # Chargement différé
│   ├── test_ai_*.py         # Tests du module IA
│   └── test_models_*.py     # Tests des modèles SQLAlchemy
│
├── services/                # Tests des services métier
│   ├── test_recettes_service.py    # ⭐ Service critique
│   ├── test_courses_service.py     # ⭐ Service critique
│   ├── test_planning_service.py    # ⭐ Service critique
│   ├── test_base_service.py        # Service de base
│   ├── test_base_ai_service.py     # Service IA de base
│   ├── test_openfoodfacts.py       # OpenFoodFacts
│   └── test_factures_ocr.py        # OCR Factures
│
├── modules/                 # Tests des modules UI
│   ├── test_energie.py      # Module énergie
│   └── test_jules_planning.py # Planning Jules
│
├── e2e/                     # Tests end-to-end
│   └── test_workflows.py    # Workflows complets
│
├── ui/                      # Tests composants UI
│   └── (à implémenter)
│
└── utils/                   # Tests utilitaires
    └── (à implémenter)
```

## Convention de nommage

### Fichiers de test

- `test_{module}_service.py` - Tests d'un service
- `test_{module}.py` - Tests d'un module/composant
- `test_api_{type}.py` - Tests API par type

### Classes de test

- `Test{Module}Service{Category}` - Ex: `TestRecetteServiceCreate`
- `Test{Feature}` - Ex: `TestCacheExpiration`

### Méthodes de test

- `test_{action}_{condition}` - Ex: `test_creer_recette_simple`
- `test_{action}_{expected_result}` - Ex: `test_rechercher_retourne_resultats`

## Markers pytest

```python
@pytest.mark.unit          # Test unitaire rapide
@pytest.mark.integration   # Test d'intégration
@pytest.mark.slow          # Test lent (> 1s)
@pytest.mark.endpoint      # Test d'endpoint API
@pytest.mark.auth          # Test nécessitant auth
```

## Fixtures principales

### Base de données

```python
@pytest.fixture
def db(engine):
    """Session SQLite in-memory pour chaque test."""

@pytest.fixture
def mock_session(db):
    """Alias pour compatibilité."""
```

### Factories

```python
@pytest.fixture
def recette_factory(db) -> RecetteFactory:
    """Factory pour créer des recettes de test."""

@pytest.fixture
def ingredient_factory(db) -> IngredientFactory:
    """Factory pour créer des ingrédients de test."""

@pytest.fixture
def planning_factory(db) -> PlanningFactory:
    """Factory pour créer des plannings de test."""
```

### Services

```python
@pytest.fixture
def recette_service() -> RecetteService:
    """Instance du service recettes."""

@pytest.fixture
def courses_service() -> CoursesService:
    """Instance du service courses."""

@pytest.fixture
def planning_service() -> PlanningService:
    """Instance du service planning."""
```

### Mocks

```python
@pytest.fixture(autouse=True)
def mock_mistral_api(monkeypatch):
    """Mock automatique de l'API Mistral."""

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit pour tests UI."""
```

## Lancer les tests

```bash
# Tous les tests
pytest

# Avec couverture
pytest --cov=src --cov-report=html

# Tests unitaires uniquement
pytest -m unit

# Tests d'un fichier spécifique
pytest tests/services/test_recettes_service.py -v

# Tests d'une classe
pytest tests/services/test_recettes_service.py::TestRecetteServiceCreate -v

# Tests d'une méthode
pytest tests/services/test_recettes_service.py::TestRecetteServiceCreate::test_creer_recette_simple -v

# Tests en parallèle (nécessite pytest-xdist)
pytest -n auto
```

## Objectifs de couverture

| Module                     | Objectif | Actuel |
| -------------------------- | -------- | ------ |
| `src/services/recettes.py` | 80%      | -      |
| `src/services/courses.py`  | 80%      | -      |
| `src/services/planning.py` | 80%      | -      |
| `src/core/database.py`     | 70%      | -      |
| `src/core/decorators.py`   | 70%      | -      |
| `src/core/ai/`             | 60%      | -      |
| **Global**                 | **50%**  | ~28%   |

## Bonnes pratiques

### ✅ À faire

- Un test = une assertion principale
- Noms explicites et en français
- Utiliser les factories pour les données de test
- Mocker les appels externes (API, DB prod)
- Tester les cas limites et erreurs

### ❌ À éviter

- Tests dépendants de l'ordre d'exécution
- Tests avec données en dur non isolées
- Tests qui modifient l'environnement global
- Tests trop longs (> 1s pour unitaire)
