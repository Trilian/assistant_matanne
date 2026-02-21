"""
Pytest Configuration & Central Fixtures
════════════════════════════════════════════════════════════════════

Fixtures partagées pour tous les tests du répertoire tests/core/.
Élimine la duplication de setup à travers les fichiers de test.

Auto-découverte: pytest charge automatiquement ce fichier.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from sqlalchemy import String, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

# ═════════════════════════════════════════════════════════════════════
# CHARGEMENT ANTICIPÉ DE TOUS LES MODÈLES
# ═════════════════════════════════════════════════════════════════════
# Nécessaire AVANT toute importation de modèle individuel pour que
# SQLAlchemy puisse résoudre les chaînes de relationship (ex: "RecipeFeedback").
try:
    from src.core.models import charger_tous_modeles

    charger_tous_modeles()
except (ImportError, Exception):
    pass

# ═════════════════════════════════════════════════════════════════════
# SECTION 1: PYTEST CONFIGURATION
# ═════════════════════════════════════════════════════════════════════


def pytest_configure(config):
    """Configure pytest avec markers personnalisés."""
    config.addinivalue_line("markers", "unit: Unit tests (fast)")
    config.addinivalue_line("markers", "integration: Integration tests (slower)")
    config.addinivalue_line("markers", "slow: Slow tests (require optimization)")
    config.addinivalue_line("markers", "requires_db: Require database")
    config.addinivalue_line("markers", "requires_redis: Require Redis")


# ═════════════════════════════════════════════════════════════════════
# SECTION 2: DATABASE FIXTURES
# ═════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="function")
def test_db() -> Session:
    """Fixture BD SQLite en mémoire pour tests isolés.

    Chaque test obtient sa propre BD fraîche.
    Auto-cleanup après le test.
    """
    from sqlalchemy import Text
    from sqlalchemy.ext.compiler import compiles

    # Adapter les types PostgreSQL pour SQLite
    try:
        from sqlalchemy.dialects.postgresql import ARRAY, JSONB

        @compiles(JSONB, "sqlite")
        def _compile_jsonb_sqlite(element, compiler, **kw):
            return "TEXT"

        @compiles(ARRAY, "sqlite")
        def _compile_array_sqlite(element, compiler, **kw):
            return "TEXT"
    except ImportError:
        pass

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    # Créer tables si modèles disponibles
    try:
        from src.core.models import Base

        Base.metadata.create_all(engine)
    except (ImportError, Exception):
        # Models pas disponibles en test mode
        pass

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    # Cleanup
    session.close()
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_with_sample_data(test_db: Session) -> Session:
    """Fixture BD avec données de test pré-chargées."""
    # Peut être étendu avec données de setup
    yield test_db


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
    model.created_at = None
    model.updated_at = None
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
# SECTION 4: STREAMLIT FIXTURES
# ═════════════════════════════════════════════════════════════════════


@pytest.fixture
def streamlit_session() -> MagicMock:
    """Mock Streamlit session_state.

    Usage:
        def test_something(streamlit_session):
            streamlit_session['key'] = 'value'
            assert streamlit_session['key'] == 'value'
    """
    with patch("streamlit.session_state", MagicMock()) as mock:
        yield mock


@pytest.fixture
def streamlit_session_with_data() -> MagicMock:
    """Mock Streamlit session_state avec données initiales."""
    session_data = {
        "user_id": "test_user",
        "user_name": "Test User",
        "session_state": "initialized",
    }
    with patch("streamlit.session_state", session_data) as mock:
        yield mock


# ═════════════════════════════════════════════════════════════════════
# SECTION 5: TEST DATA FIXTURES
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


@pytest.fixture
def test_query_info() -> dict:
    """Données query info test."""
    return {
        "sql": "SELECT * FROM users",
        "operation": "SELECT",
        "table": "users",
        "duration_ms": 10,
    }


# ═════════════════════════════════════════════════════════════════════
# SECTION 6: CLEANUP FIXTURES
# ═════════════════════════════════════════════════════════════════════


@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup automatique après chaque test."""
    yield
    # Cleanup code ici si nécessaire


@pytest.fixture
def temp_env_vars():
    """Context manager pour variables d'environnement temporaires.

    Usage:
        def test_something(temp_env_vars):
            temp_env_vars['MY_VAR'] = 'value'
            # test code
    """
    import os

    env_backup = os.environ.copy()

    yield os.environ

    # Restore
    os.environ.clear()
    os.environ.update(env_backup)


# ═════════════════════════════════════════════════════════════════════
# SECTION 7: CONTEXT MANAGER FIXTURES
# ═════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_database():
    """Context manager pour mock database."""
    from tests.core.helpers import mock_database_session

    with mock_database_session() as (session, query):
        yield session, query


@pytest.fixture
def mock_redis_connection():
    """Context manager pour mock redis."""
    from tests.core.helpers import mock_redis_connection

    with mock_redis_connection(available=True) as redis:
        yield redis


# ═════════════════════════════════════════════════════════════════════
# SECTION 8: HELPER FIXTURES
# ═════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_builder():
    """Fixture pour accéder à MockBuilder."""
    from tests.core.helpers import MockBuilder

    return MockBuilder


@pytest.fixture
def assertion_helpers():
    """Fixture pour accéder aux assertion helpers."""
    from tests.core.helpers import AssertionHelpers

    return AssertionHelpers


@pytest.fixture
def parametrize_helpers():
    """Fixture pour accéder aux parametrize helpers."""
    from tests.core.helpers import ParametrizeHelpers

    return ParametrizeHelpers


@pytest.fixture
def test_patterns():
    """Fixture pour accéder aux test patterns."""
    from tests.core.helpers import TestPatterns

    return TestPatterns


@pytest.fixture
def test_utils():
    """Fixture pour accéder aux test utils."""
    from tests.core.helpers import TestUtils

    return TestUtils


# ═════════════════════════════════════════════════════════════════════
# SECTION 9: PYTEST PLUGINS & HOOKS
# ═════════════════════════════════════════════════════════════════════


def pytest_collection_modifyitems(config, items):
    """Modifie items collectés pour ajouter defaults."""
    for item in items:
        # Marquer tous les tests sans marker comme "unit"
        if not any(
            marker.name in ["unit", "integration", "slow"] for marker in item.iter_markers()
        ):
            item.add_marker(pytest.mark.unit)


def pytest_runtest_logreport(report):
    """Hook pour logging des résultats de test."""
    if report.when == "call":
        if report.failed:
            # Log failures
            pass
        elif report.passed:
            # Log passes
            pass


# ═════════════════════════════════════════════════════════════════════
# SECTION 10: FIXTURES SCOPE
# ═════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def session_data():
    """Données au niveau session (partagées entre tests).

    Utilisé pour données lourdes à setup une seule fois.
    """
    return {
        "initialized": True,
        "timestamp": __import__("datetime").datetime.now(),
    }


@pytest.fixture(scope="module")
def module_db():
    """BD partagée au niveau module (attention: isoler les données!)."""
    engine = create_engine("sqlite:///:memory:")
    try:
        from src.core.models import Base

        Base.metadata.create_all(engine)
    except (ImportError, Exception):
        pass

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    engine.dispose()


# ═════════════════════════════════════════════════════════════════════
# SECTION 11: PYTEST INI CONFIGURATION
# ═════════════════════════════════════════════════════════════════════

"""
pytest.ini content (should be in root):

[pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
    requires_db: Requires database
    requires_redis: Requires Redis
addopts = -v --tb=short --strict-markers
"""
