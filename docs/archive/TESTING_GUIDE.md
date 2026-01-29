# Guide d'Exécution des Tests et Amélioration de la Couverture

## Étape 1: Configuration de l'Environnement de Test

### Installation des Dépendances

```bash
# Installer les dépendances requises
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio -U

# Vérifier les installations
pytest --version
python -m pytest --co  # Lister les tests
```

### Configuration pytest (pyproject.toml)

Assurez-vous que `pyproject.toml` contient:

```ini
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
asyncio_mode = "auto"

markers =
    unit: Tests unitaires sans BD
    integration: Tests avec BD et services
    e2e: Tests end-to-end (flux complets)
    services: Tests des services métier
    ui: Tests des composants UI
    core: Tests du noyau applicatif
    slow: Tests qui prennent du temps
    skip_in_ci: À ignorer dans les pipelines CI
```

## Étape 2: Exécuter les Tests et Mesurer la Couverture

### Commandes de Base

```bash
# Tous les tests
pytest tests/ -v

# Tests avec rapport de couverture
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

# Tests par répertoire
pytest tests/core/ -v
pytest tests/services/ -v
pytest tests/ui/ -v
pytest tests/integration/ -v
pytest tests/utils/ -v

# Tests par marqueur
pytest -m unit
pytest -m integration
pytest -m e2e
```

### Interpréter le Rapport de Couverture

```
Name                                Stmts   Miss  Cover   Missing
================================================================
src/core/config.py                   120    25    79%     45-48,102-110
src/services/recettes.py             250    30    88%     120-125,200-210
src/ui/components/atoms.py           180    15    92%     60-65,150
src/domains/maison/logic/jardin.py   80     50    37%     10-40,70-80  <- À AMÉLIORER
...
```

Les fichiers avec `Cover < 50%` sont prioritaires pour amélioration.

## Étape 3: Identifier les Fichiers Manquants de Tests

Fichiers du `src/` sans couverture adéquate:

### 🔴 PRIORITÉ 1 - Créer des tests (0% couverture):
1. `src/domains/maison/ui/*.py` - Module maison UI
2. `src/domains/maison/logic/*.py` - Module maison logique
3. Certains fichiers dans `src/app.py`

### 🟠 PRIORITÉ 2 - Améliorer (< 40% couverture):
1. `src/api/rate_limiting.py`
2. `src/services/weather.py`
3. `src/services/budget.py`
4. Certains modules dans `src/domains/`

### 🟡 PRIORITÉ 3 - Optimiser (40-70% couverture):
1. `src/ui/tablet_mode.py`
2. `src/core/multi_tenant.py`
3. `src/core/offline.py`

## Étape 4: Modèles de Tests à Créer

### 4.1 Tests pour Modules Domaine (Maison)

Créer `tests/domains/maison/test_jardin_module.py`:

```python
"""Tests pour le module Jardin (domaine Maison)."""

import pytest
from sqlalchemy.orm import Session
from src.domains.maison.logic.jardin_logic import (
    obtenir_plantes,
    ajouter_plante,
    mettre_a_jour_plante,
)
from src.core.models import Plante


class TestJardinLogic:
    """Tests pour la logique jardin."""
    
    def test_obtenir_plantes_vide(self, test_db: Session):
        """Test quand aucune plante."""
        result = obtenir_plantes(test_db)
        assert result == []
    
    def test_ajouter_plante(self, test_db: Session):
        """Test ajouter une plante."""
        result = ajouter_plante(
            test_db,
            nom="Tomate",
            type_plante="légume",
            zone_id=1
        )
        assert result.nom == "Tomate"
        assert result.type_plante == "légume"
    
    def test_mettre_a_jour_plante(self, test_db: Session):
        """Test mettre à jour une plante."""
        # Setup
        plante = ajouter_plante(test_db, "Rose", "fleur", 1)
        
        # Action
        result = mettre_a_jour_plante(
            test_db,
            plante.id,
            arrosee=True
        )
        
        # Assert
        assert result.arrosee is True


@pytest.mark.integration
class TestJardinModule:
    """Tests d'intégration pour le module jardin."""
    
    def test_jardin_module_app(self):
        """Test que le module jardin se charge."""
        from src.domains.maison.ui.jardin import app
        assert callable(app)
```

### 4.2 Tests pour Services Métier

Créer `tests/services/test_weather_extended.py`:

```python
"""Tests étendus pour le service météo."""

import pytest
from src.services.weather import WeatherService


class TestWeatherService:
    """Tests pour WeatherService."""
    
    def test_get_weather_coordinates(self):
        """Test récupération météo par coordonnées."""
        service = WeatherService()
        result = service.get_weather(lat=48.8566, lon=2.3522)
        
        assert result is not None
        assert "temperature" in result
        assert "conditions" in result
    
    def test_get_weather_invalid_coords(self):
        """Test avec coordonnées invalides."""
        service = WeatherService()
        
        with pytest.raises(ValueError):
            service.get_weather(lat=999, lon=999)
```

### 4.3 Tests pour UI Components

Créer `tests/ui/test_tablet_mode.py`:

```python
"""Tests pour le mode tablette."""

import pytest
import streamlit as st


class TestTabletMode:
    """Tests pour la gestion du mode tablette."""
    
    def test_is_tablet_mode_default(self):
        """Test détection tablette par défaut."""
        from src.ui.tablet_mode import is_tablet_mode
        
        result = is_tablet_mode()
        assert isinstance(result, bool)
    
    def test_set_tablet_mode(self):
        """Test définition du mode tablette."""
        from src.ui.tablet_mode import set_tablet_mode
        
        set_tablet_mode(True)
        # Vérifier que le mode est défini
        # (dépend de l'implémentation)
```

## Étape 5: Stratégies d'Amélioration Rapide

### Approche 1: Tests Paramétrisés (Gain 10-15%)

Au lieu de:
```python
def test_formatter_100():
    assert format_number(100) == "100"

def test_formatter_1000():
    assert format_number(1000) == "1 000"

def test_formatter_1000000():
    assert format_number(1000000) == "1 000 000"
```

Utiliser:
```python
@pytest.mark.parametrize("value,expected", [
    (100, "100"),
    (1000, "1 000"),
    (1000000, "1 000 000"),
    (0, "0"),
    (-100, "-100"),
])
def test_format_number(value, expected):
    assert format_number(value) == expected
```

### Approche 2: Fixtures Réutilisables (Gain 5-10%)

Créer `tests/conftest.py` (ou améliorer l'existant):

```python
import pytest
from sqlalchemy import create_engine
from src.core.database import Session


@pytest.fixture(scope="function")
def test_db():
    """BD de test (SQLite en mémoire)."""
    engine = create_engine("sqlite:///:memory:")
    # Créer les tables
    # ...
    yield Session(engine)


@pytest.fixture
def sample_recipe():
    """Recette exemple pour tests."""
    return {
        "nom": "Pâtes Carbonara",
        "temps_preparation": 15,
        "difficulte": "facile",
        "ingredients": ["pâtes", "œufs", "lard"],
    }


@pytest.fixture
def sample_course_item():
    """Article de courses exemple."""
    return {
        "nom": "Lait",
        "quantite": 1,
        "unite": "L",
        "categorie": "Produits laitiers",
    }
```

### Approche 3: Mocking Streamlit (Gain 3-5%)

```python
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_st():
    """Mock Streamlit pour éviter l'UI."""
    with patch("streamlit.session_state", new_callable=MagicMock):
        yield
```

## Étape 6: Checklist de Couverture à 40%

Vérifier que vous avez couverture pour:

- [ ] **Utils** (helpers, formatters, validators): 90%+
- [ ] **Core** (config, database, cache, decorators): 80%+
- [ ] **Services** (recettes, courses, planning): 80%+
- [ ] **UI Components**: 75%+
- [ ] **API endpoints**: 70%+
- [ ] **Domains** (cuisine, famille, planning): 50%+
- [ ] **Logic** (logique métier): 40%+
- [ ] **E2E** (tests complets): 20%+
- [ ] **App.py principal**: 30%+

## Étape 7: Exécution de la Couverture

```bash
# Exécuter et générer rapport HTML
pytest tests/ \
    --cov=src \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-report=xml

# Ouvrir le rapport
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac
xdg-open htmlcov/index.html  # Linux
```

## Étape 8: Amélioration Progressive

### Semaine 1: Créer 10 nouveaux fichiers de test
- [ ] `tests/domains/maison/` - 4 fichiers
- [ ] `tests/services/` - 3 fichiers améliorés
- [ ] `tests/e2e/` - 3 fichiers
- **Résultat attendu:** +5-8% couverture

### Semaine 2: Paramétrer les tests existants
- [ ] Convertir 20 tests simples en tests paramétrisés
- [ ] Ajouter plus de cas edge
- **Résultat attendu:** +3-5% couverture

### Semaine 3: Couvrir les logiques complexes
- [ ] Tests pour les domaines manquants
- [ ] Tests pour la logique IA
- **Résultat attendu:** +5-10% couverture

**Total attendu: 40%+**

## Commandes Rapides à Retenir

```bash
# Couverture rapide
pytest tests/ --cov=src --cov-report=term

# Couverture détaillée
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Tests spécifiques avec couverture
pytest tests/services/ --cov=src.services --cov-report=term

# Tests rapides (skip les lents)
pytest tests/ -m "not slow" -v

# Avec sortie succincte
pytest tests/ -q --tb=no
```

## Ressources

- [pytest documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)

---

**Guide créé:** 2026-01-29  
**Prochain checkpoint:** Mesurer la couverture après implémentation
