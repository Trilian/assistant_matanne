"""
TEST MAINTENANCE & BEST PRACTICES GUIDE
════════════════════════════════════════════════════════════════════

Guide complet pour maintenir et évoluer la suite de tests.
Inclut patterns réutilisables, checklist, et procédures.
"""

# ═════════════════════════════════════════════════════════════════════
# SECTION 1: OVERVIEW
# ═════════════════════════════════════════════════════════════════════

## Organisation de Test Suite

La suite de test est organisée en 5 phases:

- **Phase 1**: Core Utilities (errors, logging, constants, config, validation)
- **Phase 2**: ORM Models (SQLAlchemy models et relationships)
- **Phase 3**: AI & Services (client IA, analyse)
- **Phase 4**: Offline & Performance (sync, notifications, perf, decorators, lazy)
- **Phase 5**: Infrastructure (multi-tenant, redis-cache, sql-optimizer)

**Structure:**
```
tests/core/
├── conftest.py           # Fixtures centralisées
├── helpers.py            # Builders et utilitaires (NOUVEAU)
├── test_*.py            # Fichiers de test (18 fichiers)
```

**Status:** ✅ 684+ tests, ~85% coverage, production-ready


# ═════════════════════════════════════════════════════════════════════
# SECTION 2: PATTERNS RÉUTILISABLES
# ═════════════════════════════════════════════════════════════════════

## Pattern 1: Création de Mocks Standardisée

❌ **AVANT (Redondant):**
```python
def setup_method(self):
    self.session = Mock(spec=Session)
    self.session.add = Mock()
    self.session.delete = Mock()
    self.session.commit = Mock()
    self.session.rollback = Mock()
```

✅ **APRÈS (Utiliser helpers):**
```python
from tests.core.helpers import MockBuilder

def setup_method(self):
    self.session = MockBuilder.create_session_mock()
    self.query = MockBuilder.create_query_mock()
```

**Builders Disponibles:**
- `MockBuilder.create_session_mock()` - SQLAlchemy Session
- `MockBuilder.create_query_mock()` - SQLAlchemy Query
- `MockBuilder.create_model_mock()` - ORM Model
- `MockBuilder.create_redis_mock()` - Redis Client


## Pattern 2: Context Managers pour Mocking

❌ **AVANT (Répété dans ~30 tests):**
```python
def test_something(self):
    mock_session = MagicMock()
    with patch("streamlit.session_state", mock_session):
        # test code
```

✅ **APRÈS:**
```python
from tests.core.helpers import mock_streamlit_session

def test_something(self):
    with mock_streamlit_session() as session:
        # test code
```

**Context Managers Disponibles:**
- `mock_streamlit_session()` - Streamlit session_state
- `mock_redis_connection()` - Redis connection
- `mock_database_session()` - Database session
- `mock_logger_context()` - Logger


## Pattern 3: Test Data Factory

❌ **AVANT (Hardcodé partout):**
```python
def test_user():
    user_data = {
        'id': '123',
        'name': 'Test User',
        'email': 'test@example.com'
    }
```

✅ **APRÈS:**
```python
from tests.core.helpers import create_test_data

def test_user():
    user_data = create_test_data('user_dict')
    # ou avec customization:
    user_data = create_test_data('user_dict', name='Custom Name')
```

**Data Types Disponibles:**
- `'user_dict'` - Données utilisateur
- `'recipe_dict'` - Données recette
- `'cache_entry'` - Entrée cache
- `'query_info'` - Info requête SQL


## Pattern 4: Assertions Lisibles

❌ **AVANT (Verbeux):**
```python
assert mock.call_count == 1
assert mock.call_count == 1, f"Expected 1 call"
```

✅ **APRÈS:**
```python
from tests.core.helpers import AssertionHelpers

AssertionHelpers.assert_mock_called_once_with_args(mock, arg1, arg2)
AssertionHelpers.assert_dict_has_keys(data, ['id', 'name', 'email'])
```

**Helpers Disponibles:**
- `assert_mock_called_once_with_args()`
- `assert_mock_not_called()`
- `assert_mock_called_n_times()`
- `assert_dict_has_keys()`
- `assert_list_contains()`
- `assert_str_contains()`


## Pattern 5: Fixtures Centralisées

❌ **AVANT (Dupliquées dans chaque fichier):**
```python
# Dans test_file1.py
@pytest.fixture
def mock_session():
    return Mock(spec=Session)

# Dans test_file2.py
@pytest.fixture
def mock_session():
    return Mock(spec=Session)
```

✅ **APRÈS (Dans helpers.py):**
```python
# Tests utilisent:
from tests.core.helpers import mock_session  # @pytest.fixture

def test_something(mock_session):
    ...
```

**Fixtures Disponibles:**
- `mock_session` - Mock Session
- `mock_query` - Mock Query
- `mock_model` - Mock Model
- `mock_redis` - Mock Redis
- `streamlit_session` - Mock Streamlit
- `test_db` - Fixture BD réelle (SQLite)
- `test_user_data` - Données test utilisateur


# ═════════════════════════════════════════════════════════════════════
# SECTION 3: CHECKLIST DE MAINTENANCE MENSUELLE
# ═════════════════════════════════════════════════════════════════════

## Semaine 1: Analyse

- [ ] Exécuter rapport maintenance: `python scripts/manage_tests.py analyze`
- [ ] Vérifier couverture: `pytest tests/core/ --cov=src/core`
- [ ] Chercher redondances: `python scripts/manage_tests.py refactor`
- [ ] Vérifier structure: `python scripts/manage_tests.py validate`

## Semaine 2: Code Review

- [ ] Revoir suggestions de refactorisation
- [ ] Identifier patterns dupliqués
- [ ] Vérifier fixtures inutilisées
- [ ] Analyser tests lents

## Semaine 3: Refactorisation

- [ ] Migrer mocks vers MockBuilder
- [ ] Consolidate fixtures inutilisées
- [ ] Refactoriser patterns redondants
- [ ] Ajouter tests manquants

## Semaine 4: Validation

- [ ] Exécuter tous les tests: `pytest tests/core/ -v`
- [ ] Vérifier couverture > 85%
- [ ] Générer rapport final: `python scripts/manage_tests.py report`
- [ ] Documenter changements


# ═════════════════════════════════════════════════════════════════════
# SECTION 4: AJOUTER UN NOUVEAU TEST
# ═════════════════════════════════════════════════════════════════════

## Template Standard

```python
"""
Module docstring: Tests pour [module_name]
Couvre: [features à tester]
"""

import pytest
from unittest.mock import Mock, patch
from tests.core.helpers import (
    MockBuilder, mock_streamlit_session,
    AssertionHelpers, create_test_data
)


# ═════════════════════════════════════════════════════════════════════
# SECTION 1: IMPORTS & SETUP
# ═════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="function")
def setup_env():
    """Setup pour tous les tests."""
    # Fixture setup here
    yield
    # Cleanup here


# ═════════════════════════════════════════════════════════════════════
# SECTION 2: CORE FUNCTIONALITY
# ═════════════════════════════════════════════════════════════════════

class TestCoreFeature:
    """Tests pour fonctionnalité core."""
    
    def setup_method(self):
        """Setup avant chaque test."""
        self.session = MockBuilder.create_session_mock()
    
    @pytest.mark.unit
    def test_feature_success(self):
        """Test cas nominal."""
        # Arrange
        data = create_test_data('user_dict')
        
        # Act
        result = do_something(data, self.session)
        
        # Assert
        assert result is not None
        AssertionHelpers.assert_mock_called_once_with_args(
            self.session.add, pytest.any()
        )


# ═════════════════════════════════════════════════════════════════════
# SECTION 3: EDGE CASES
# ═════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Tests pour cas limites."""
    
    @pytest.mark.unit
    @pytest.mark.parametrize("input_val", [None, "", "   "])
    def test_empty_input(self, input_val):
        """Test inputs vides."""
        with pytest.raises(ValueError):
            do_something(input_val)
```

## Checklist Nouveau Test

- [ ] Utiliser MockBuilder pour mocks
- [ ] Utiliser context managers pour patching
- [ ] Ajouter @pytest.mark.unit ou .integration
- [ ] Couvrir normal + edge cases
- [ ] Utiliser create_test_data pour données
- [ ] Ajouter docstring descriptive
- [ ] Vérifier couverture augmente
- [ ] Pas de setup_method dupliqué


# ═════════════════════════════════════════════════════════════════════
# SECTION 5: METTRE À JOUR UN TEST EXISTANT
# ═════════════════════════════════════════════════════════════════════

## Procédure Quand Code Source Change

```
1. Identifier le module affecté:
   $ git diff --name-only HEAD~1

2. Trouver test correspondant:
   $ ls tests/core/test_[module].py

3. Exécuter test:
   $ pytest tests/core/test_[module].py -v

4. Si échec, mettre à jour test:
   a) Analyser nouveau code
   b) Ajouter/modifier assertions
   c) Ajouter edge cases si nécessaire

5. Vérifier mocks toujours appropriés:
   $ grep -n "Mock(" tests/core/test_[module].py

6. Re-exécuter tests:
   $ pytest tests/core/test_[module].py -v

7. Commit avec message:
   "fix: Update tests for [module] changes"
```

## Anti-patterns à Éviter

- ❌ Hardcoder des valeurs au lieu d'utiliser create_test_data
- ❌ Dupliquer setup_method d'autre classe
- ❌ Créer Mock() inline au lieu d'utiliser MockBuilder
- ❌ Avoir du code mort ou inutilisé
- ❌ Tests sans @pytest.mark
- ❌ Fixtures définies dans chaque fichier
- ❌ Pas de docstring


# ═════════════════════════════════════════════════════════════════════
# SECTION 6: REFACTORISATION PROGRESSIVE
# ═════════════════════════════════════════════════════════════════════

## Phase de Migration Vers Helpers.py

### Phase 1: Analyse (FAIT ✅)
- Créer helpers.py avec patterns courants
- Identifier redondances
- Générer rapport

### Phase 2: Migration Graduelle
```bash
# Test fichier par fichier
pytest tests/core/test_errors.py -v
# Migrer imports
# Vérifier passage
```

### Phase 3: Consolidation
```python
# Avant
def setup_method(self):
    self.session = Mock(spec=Session)
    self.session.add = Mock()
    ...

# Après
from tests.core.helpers import MockBuilder

def setup_method(self):
    self.session = MockBuilder.create_session_mock()
```

### Phase 4: Validation
```bash
pytest tests/core/ --cov=src/core -v
# Vérifier couverture maintenue > 85%
```

## Timeline Recommandée

- Semaine 1: test_errors.py, test_logging.py
- Semaine 2: test_config.py, test_constants.py
- Semaine 3: test_models_*.py
- Semaine 4: test_ai_*.py
- Semaine 5: test_redis_cache.py, test_multi_tenant.py
- Semaine 6: Tous les autres


# ═════════════════════════════════════════════════════════════════════
# SECTION 7: OUTILS DE MAINTENANCE
# ═════════════════════════════════════════════════════════════════════

## Scripts Disponibles

### Analyse
```bash
# Rapport complet
python scripts/manage_tests.py analyze

# Suggestions refactorisation
python scripts/manage_tests.py refactor

# Rapport en JSON
python scripts/manage_tests.py report
```

### Validation
```bash
# Vérifier structure
python scripts/manage_tests.py validate

# Vérifier dépendances
python scripts/manage_tests.py update
```

### Commandes Pytest

```bash
# Tous les tests
pytest tests/core/ -v

# Avec couverture
pytest tests/core/ --cov=src/core --cov-report=html

# Unitaires seulement
pytest tests/core/ -m unit

# Intégration seulement
pytest tests/core/ -m integration

# Un fichier spécifique
pytest tests/core/test_redis_cache.py -v

# Un test spécifique
pytest tests/core/test_redis_cache.py::TestRedisCache::test_get_set -v

# Watch mode (auto-rerun)
pytest-watch tests/core/ -- -v
```


# ═════════════════════════════════════════════════════════════════════
# SECTION 8: DOCUMENTATION DES TESTS
# ═════════════════════════════════════════════════════════════════════

## Docstring Format

```python
def test_cache_invalidation_with_tags(self):
    """Test que les tags invalident correctement le cache.
    
    Scenario:
        - Créer 3 entrées cache avec tags communs
        - Invalider par tag
        - Vérifier entrées supprimées
    
    Expected:
        Toutes les entrées avec le tag sont supprimées
        Les autres restent intactes
    """
    # Test code
```

## Docstring Sections

- **Description**: Une ligne brève
- **Scenario**: Comment le test fonctionne
- **Expected**: Résultat attendu
- **Edge Cases**: Cas limites couverts


# ═════════════════════════════════════════════════════════════════════
# SECTION 9: CI/CD INTEGRATION
# ═════════════════════════════════════════════════════════════════════

## GitHub Actions Workflow

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests with coverage
        run: pytest tests/core/ --cov=src/core --cov-report=term-missing
      
      - name: Check coverage
        run: pytest tests/core/ --cov=src/core --cov-fail-under=85
      
      - name: Run maintenance check
        run: python scripts/manage_tests.py validate
```

## Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

pytest tests/core/ -x -q
if [ $? -ne 0 ]; then
    echo "Tests failed - commit blocked"
    exit 1
fi
```


# ═════════════════════════════════════════════════════════════════════
# SECTION 10: TROUBLESHOOTING
# ═════════════════════════════════════════════════════════════════════

## Test échoue

1. **Vérifier le message d'erreur**
   ```bash
   pytest tests/core/test_[module].py::TestClass::test_name -vv
   ```

2. **Ajouter print debug**
   ```bash
   pytest tests/core/test_[module].py -vv -s
   ```

3. **Vérifier mock setup**
   - Mock a-t-il les bons return_value?
   - Les assertions utilisent-elles les bons mocks?

4. **Comparer avec pattern réussi**
   ```bash
   grep -A 10 "test_success" tests/core/test_*.py
   ```

## Couverture baisse

1. **Identifier tests manquants**
   ```bash
   pytest tests/core/ --cov=src/core --cov-report=term-missing | grep "^MISSING"
   ```

2. **Ajouter tests manquants**
   - Revoir la ligne manquante
   - Ajouter cas test

3. **Vérifier mocking complet**
   - Tous les appels externes mockés?
   - Tous les paths d'erreur testés?

## Tests lents

1. **Identifier tests lents**
   ```bash
   pytest tests/core/ --durations=20
   ```

2. **Optimiser**
   - Réduire setup complexe
   - Utiliser mocks au lieu données réelles
   - Regrouper tests

3. **Ajouter marker**
   ```python
   @pytest.mark.slow
   def test_expensive_operation(self):
       ...
   ```


# ═════════════════════════════════════════════════════════════════════
# SECTION 11: RESSOURCES
# ═════════════════════════════════════════════════════════════════════

## Fichiers Clés

- **tests/core/helpers.py** - Patterns réutilisables
- **tests/core/conftest.py** - Fixtures centralisées
- **scripts/manage_tests.py** - Outils maintenance
- **TESTS_COVERAGE_PHASE5_COMPLETE.md** - Rapport complet

## Commandes Rapides

```bash
# Tout en un
pytest tests/core/ --cov=src/core -v && python scripts/manage_tests.py report

# Maintenance complète
python scripts/manage_tests.py analyze
python scripts/manage_tests.py refactor
python scripts/manage_tests.py validate
```

## References

- [pytest docs](https://docs.pytest.org/)
- [unittest.mock docs](https://docs.python.org/3/library/unittest.mock.html)
- [SQLAlchemy testing](https://docs.sqlalchemy.org/en/14/orm/session_basics.html)


════════════════════════════════════════════════════════════════════════

**SUMMARY**: 
- 684+ tests couvrent 85% src/core
- Patterns réutilisables dans helpers.py
- Scripts maintenance automatisés
- Prêt pour production et scaling

**Next Steps**:
- Migrer progressivement vers helpers.py
- Ajouter tests pour nouvelles features
- Maintenir couverture > 85%
- Exécuter checklist maintenance mensuelle
"""
