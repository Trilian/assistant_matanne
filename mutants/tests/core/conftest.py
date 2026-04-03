"""
Pytest Configuration & Fixtures for tests/core/
════════════════════════════════════════════════════════════════════

Fixtures partagées pour tous les tests du répertoire tests/core/.
REMARQUE: La majorité des fixtures viennent de tests/conftest.py root.
Ce fichier ne fournit que les fixtures core-spécifiques.

Auto-découverte: pytest charge automatiquement ce fichier.
"""

from unittest.mock import MagicMock, Mock

import pytest

# ═════════════════════════════════════════════════════════════════════
# CHARGEMENT ANTICIPÉ DE TOUS LES MODÈLES
# ═════════════════════════════════════════════════════════════════════
# Nécessaire AVANT toute importation de modèle individuel pour que
# SQLAlchemy puisse résoudre les chaînes de relationship (ex: "RetourRecette").
try:
    from src.core.models import charger_tous_modeles

    charger_tous_modeles()
except (ImportError, Exception):
    pass


# ═════════════════════════════════════════════════════════════════════
# SECTION 3: MOCK FIXTURES
# ═════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_session() -> Mock:
    """Mock Session SQLAlchemy avec methods communes."""
    session = Mock(spec=Session)
    session.add = Mock()
    session.delete = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.flush = Mock()
    session.close = Mock()
    session.query = Mock()
    session.execute = Mock()
    return session


@pytest.fixture
def mock_query() -> Mock:
    """Mock Query SQLAlchemy avec chainable methods."""
    query = Mock()
    query.filter = Mock(return_value=query)
    query.filter_by = Mock(return_value=query)
    query.all = Mock(return_value=[])
    query.first = Mock(return_value=None)
    query.one = Mock(return_value=None)
    query.count = Mock(return_value=0)
    query.order_by = Mock(return_value=query)
    query.limit = Mock(return_value=query)
    query.offset = Mock(return_value=query)
    query.join = Mock(return_value=query)
    query.distinct = Mock(return_value=query)
    return query


@pytest.fixture
def mock_model() -> Mock:
    """Mock ORM Model."""
    model = Mock()
    model.id = 1
    model.cree_le = None
    model.modifie_le = None
    return model


@pytest.fixture
def mock_redis() -> Mock:
    """Mock Redis Client."""
    redis = Mock()
    redis.get = Mock(return_value=None)
    redis.set = Mock(return_value=True)
    redis.delete = Mock(return_value=1)
    redis.exists = Mock(return_value=False)
    redis.keys = Mock(return_value=[])
    redis.expire = Mock(return_value=True)
    redis.ttl = Mock(return_value=-1)
    redis.ping = Mock(return_value=True)
    redis.close = Mock()
    return redis


@pytest.fixture
def mock_logger() -> MagicMock:
    """Mock Logger."""
    return MagicMock()


# ═════════════════════════════════════════════════════════════════════
# SECTION 4: TEST DATA FIXTURES
# ═════════════════════════════════════════════════════════════════════


@pytest.fixture
def test_user_data() -> dict:
    """Données utilisateur test."""
    return {
        "id": "123",
        "name": "Test User",
        "email": "test@example.com",
    }


@pytest.fixture
def test_recipe_data() -> dict:
    """Données recette test."""
    return {
        "id": 1,
        "nom": "Test Recipe",
        "ingredients": ["ingredient1", "ingredient2"],
        "instructions": "Step 1...",
    }


@pytest.fixture
def test_cache_entry() -> dict:
    """Données cache entry test."""
    return {
        "key": "test:key",
        "value": "test_value",
        "ttl": 3600,
        "tags": ["tag1", "tag2"],
    }
