"""
Test Helpers & Utilities - Consolidated Reusable Patterns
════════════════════════════════════════════════════════════════════

Centralisation des patterns réutilisables pour éviter duplication dans les tests.
Ce fichier contient les utilitaires communs, fixtures, et builders pour tests.

Usage:
    from tests.core.helpers import (
        MockSessionBuilder, StreamlitMockContext, 
        create_mock_model, create_test_db
    )
"""

from unittest.mock import Mock, MagicMock, patch, AsyncMock
from contextlib import contextmanager
from typing import Any, Dict, Type, Optional, Generator
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


# ═════════════════════════════════════════════════════════════════════
# SECTION 1: BUILDERS POUR MOCKS
# ═════════════════════════════════════════════════════════════════════

class MockBuilder:
    """Builder pour créer des mocks cohérents et maintenables."""

    @staticmethod
    def create_session_mock(**kwargs) -> Mock:
        """Crée un mock Session SQLAlchemy avec methods communes."""
        session = Mock(spec=Session)
        session.add = Mock()
        session.delete = Mock()
        session.commit = Mock()
        session.rollback = Mock()
        session.flush = Mock()
        session.close = Mock()
        session.query = Mock()
        session.execute = Mock()
        
        # Apply custom attributes
        for key, value in kwargs.items():
            setattr(session, key, value)
        
        return session

    @staticmethod
    def create_query_mock(return_value: Optional[Any] = None) -> Mock:
        """Crée un mock Query SQLAlchemy avec chainable methods."""
        query = Mock()
        query.filter = Mock(return_value=query)
        query.filter_by = Mock(return_value=query)
        query.all = Mock(return_value=return_value or [])
        query.first = Mock(return_value=return_value)
        query.one = Mock(return_value=return_value)
        query.count = Mock(return_value=len(return_value or []))
        query.order_by = Mock(return_value=query)
        query.limit = Mock(return_value=query)
        query.offset = Mock(return_value=query)
        query.join = Mock(return_value=query)
        query.distinct = Mock(return_value=query)
        query.select_from = Mock(return_value=query)
        
        return query

    @staticmethod
    def create_model_mock(model_class: Optional[Type] = None, **fields) -> Mock:
        """Crée un mock ORM Model avec fields personnalisés."""
        model = Mock(spec=model_class) if model_class else Mock()
        
        # Common ORM fields
        model.id = Mock()
        model.created_at = Mock()
        model.updated_at = Mock()
        
        # Apply custom fields
        for field_name, field_value in fields.items():
            setattr(model, field_name, field_value)
        
        return model

    @staticmethod
    def create_redis_mock() -> Mock:
        """Crée un mock Redis Client avec methods communes."""
        redis_mock = Mock()
        redis_mock.get = Mock(return_value=None)
        redis_mock.set = Mock(return_value=True)
        redis_mock.delete = Mock(return_value=1)
        redis_mock.exists = Mock(return_value=False)
        redis_mock.keys = Mock(return_value=[])
        redis_mock.expire = Mock(return_value=True)
        redis_mock.ttl = Mock(return_value=-1)
        redis_mock.ping = Mock(return_value=True)
        redis_mock.close = Mock()
        
        return redis_mock


# ═════════════════════════════════════════════════════════════════════
# SECTION 2: CONTEXT MANAGERS POUR MOCKING
# ═════════════════════════════════════════════════════════════════════

@contextmanager
def mock_streamlit_session():
    """Context manager pour mocker session_state Streamlit."""
    mock_session = MagicMock()
    with patch("streamlit.session_state", mock_session):
        yield mock_session


@contextmanager
def mock_redis_connection(available: bool = True):
    """Context manager pour mocker Redis connection."""
    if available:
        redis_mock = MockBuilder.create_redis_mock()
        with patch("redis.Redis", return_value=redis_mock):
            yield redis_mock
    else:
        with patch("redis.Redis", side_effect=ConnectionError("Redis unavailable")):
            yield None


@contextmanager
def mock_database_session(data: Optional[list] = None):
    """Context manager pour mocker Session BD."""
    session = MockBuilder.create_session_mock()
    query = MockBuilder.create_query_mock(return_value=data or [])
    session.query.return_value = query
    
    with patch("sqlalchemy.orm.Session", return_value=session):
        yield session, query


@contextmanager
def mock_logger_context():
    """Context manager pour mocker logger."""
    mock_logger = MagicMock()
    with patch("logging.getLogger", return_value=mock_logger):
        yield mock_logger


# ═════════════════════════════════════════════════════════════════════
# SECTION 3: FACTORY FUNCTIONS POUR DONNÉES DE TEST
# ═════════════════════════════════════════════════════════════════════

def create_test_data(data_type: str, **kwargs) -> Any:
    """Factory pour créer données de test communes."""
    factories = {
        'user_dict': lambda: {
            'id': kwargs.get('id', '123'),
            'name': kwargs.get('name', 'Test User'),
            'email': kwargs.get('email', 'test@example.com'),
            **kwargs.get('extra', {})
        },
        'recipe_dict': lambda: {
            'id': kwargs.get('id', 1),
            'nom': kwargs.get('nom', 'Test Recipe'),
            'ingredients': kwargs.get('ingredients', []),
            'instructions': kwargs.get('instructions', ''),
            **kwargs.get('extra', {})
        },
        'cache_entry': lambda: {
            'key': kwargs.get('key', 'test:key'),
            'value': kwargs.get('value', 'test_value'),
            'ttl': kwargs.get('ttl', 3600),
            'tags': kwargs.get('tags', []),
        },
        'query_info': lambda: {
            'sql': kwargs.get('sql', 'SELECT * FROM users'),
            'operation': kwargs.get('operation', 'SELECT'),
            'table': kwargs.get('table', 'users'),
            'duration_ms': kwargs.get('duration_ms', 10),
        }
    }
    
    if data_type not in factories:
        raise ValueError(f"Unknown data_type: {data_type}")
    
    return factories[data_type]()


# ═════════════════════════════════════════════════════════════════════
# SECTION 4: TEST DATABASE FIXTURES
# ═════════════════════════════════════════════════════════════════════

@pytest.fixture
def test_db() -> Generator[Session, None, None]:
    """Fixture BD en mémoire SQLite pour tests."""
    engine = create_engine('sqlite:///:memory:')
    
    # Import models pour créer tables
    try:
        from src.core.models import Base
        Base.metadata.create_all(engine)
    except ImportError:
        pass  # Models pas disponibles en test mode
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    engine.dispose()


@pytest.fixture
def test_db_with_data(test_db: Session) -> Session:
    """Fixture BD avec données de test pré-chargées."""
    # Peut être étendu avec données par défaut
    return test_db


# ═════════════════════════════════════════════════════════════════════
# SECTION 5: ASSERTIONS HELPERS
# ═════════════════════════════════════════════════════════════════════

class AssertionHelpers:
    """Helpers pour assertions courantes et lisibles."""

    @staticmethod
    def assert_mock_called_once_with_args(mock: Mock, *args, **kwargs) -> None:
        """Vérifie qu'un mock est appelé une fois avec les args spécifiés."""
        assert mock.call_count == 1, f"Expected 1 call, got {mock.call_count}"
        mock.assert_called_once_with(*args, **kwargs)

    @staticmethod
    def assert_mock_not_called(mock: Mock) -> None:
        """Vérifie qu'un mock n'a pas été appelé."""
        assert mock.call_count == 0, f"Expected 0 calls, got {mock.call_count}"

    @staticmethod
    def assert_mock_called_n_times(mock: Mock, n: int) -> None:
        """Vérifie qu'un mock est appelé exactement n fois."""
        assert mock.call_count == n, f"Expected {n} calls, got {mock.call_count}"

    @staticmethod
    def assert_dict_has_keys(data: Dict, expected_keys: list) -> None:
        """Vérifie qu'un dict contient toutes les clés attendues."""
        missing_keys = set(expected_keys) - set(data.keys())
        assert not missing_keys, f"Missing keys: {missing_keys}"

    @staticmethod
    def assert_list_contains(items: list, expected: Any) -> None:
        """Vérifie qu'une liste contient un élément."""
        assert expected in items, f"Expected {expected} in {items}"

    @staticmethod
    def assert_str_contains(text: str, substring: str) -> None:
        """Vérifie qu'une string contient une substring."""
        assert substring in text, f"Expected '{substring}' in '{text}'"


# ═════════════════════════════════════════════════════════════════════
# SECTION 6: PARAMETRIZE HELPERS
# ═════════════════════════════════════════════════════════════════════

class ParametrizeHelpers:
    """Helpers pour pytest.mark.parametrize courants."""

    # Test data sets
    VALID_STRINGS = [
        "simple_string",
        "with_spaces here",
        "with_special_chars!@#",
        "with_unicode_café",
        "with_chinese_你好",
        "very_" + "long_" * 50 + "string",
    ]

    INVALID_STRINGS = [
        "",
        None,
        "   ",
        "\n\t\r",
    ]

    VALID_IDS = [
        "123",
        "abc-def-ghi",
        "user_123",
        "UPPERCASE",
        "mixed_CASE_123",
    ]

    INVALID_IDS = [
        "",
        None,
        "   ",
    ]

    VALID_NUMBERS = [0, 1, -1, 100, 999999, 0.5, -0.5]
    INVALID_NUMBERS = [None, "string", [], {}]

    VALID_DICTS = [
        {},
        {"key": "value"},
        {"nested": {"key": "value"}},
        {"list": [1, 2, 3]},
    ]

    INVALID_DICTS = [None, [], "string", 123]

    VALID_LISTS = [[], [1], [1, 2, 3], ["a", "b", "c"]]
    INVALID_LISTS = [None, {}, "string", 123]


# ═════════════════════════════════════════════════════════════════════
# SECTION 7: COMMON TEST PATTERNS
# ═════════════════════════════════════════════════════════════════════

class TestPatterns:
    """Patterns répétés dans les tests."""

    @staticmethod
    def setup_db_test() -> tuple[Mock, Mock]:
        """Setup standard pour test DB."""
        session = MockBuilder.create_session_mock()
        query = MockBuilder.create_query_mock()
        session.query.return_value = query
        return session, query

    @staticmethod
    def setup_cache_test() -> Mock:
        """Setup standard pour test cache."""
        cache = Mock()
        cache.get = Mock(return_value=None)
        cache.set = Mock(return_value=True)
        cache.delete = Mock(return_value=True)
        cache.clear = Mock(return_value=True)
        return cache

    @staticmethod
    def setup_context_test() -> tuple[Mock, Mock]:
        """Setup standard pour test context manager."""
        context = Mock()
        context.__enter__ = Mock(return_value=context)
        context.__exit__ = Mock(return_value=False)
        return context

    @staticmethod
    def assert_db_operation_successful(session: Mock, operation: str) -> None:
        """Vérifie qu'une opération DB s'est bien déroulée."""
        if operation == 'commit':
            session.commit.assert_called_once()
        elif operation == 'rollback':
            session.rollback.assert_called_once()
        elif operation == 'flush':
            session.flush.assert_called_once()


# ═════════════════════════════════════════════════════════════════════
# SECTION 8: FIXTURES COMMUNES
# ═════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_session():
    """Fixture pour mock Session."""
    return MockBuilder.create_session_mock()


@pytest.fixture
def mock_query():
    """Fixture pour mock Query."""
    return MockBuilder.create_query_mock()


@pytest.fixture
def mock_model():
    """Fixture pour mock Model."""
    return MockBuilder.create_model_mock()


@pytest.fixture
def mock_redis():
    """Fixture pour mock Redis."""
    return MockBuilder.create_redis_mock()


@pytest.fixture
def mock_logger():
    """Fixture pour mock Logger."""
    return MagicMock()


@pytest.fixture
def streamlit_session():
    """Fixture pour mock Streamlit session_state."""
    with mock_streamlit_session() as session:
        yield session


@pytest.fixture
def test_user_data():
    """Fixture pour données utilisateur test."""
    return create_test_data('user_dict')


@pytest.fixture
def test_recipe_data():
    """Fixture pour données recette test."""
    return create_test_data('recipe_dict')


@pytest.fixture
def test_cache_entry():
    """Fixture pour données cache test."""
    return create_test_data('cache_entry')


# ═════════════════════════════════════════════════════════════════════
# SECTION 9: DECORATORS POUR TESTS
# ═════════════════════════════════════════════════════════════════════

def requires_db(test_func):
    """Décorateur pour tests nécessitant une BD."""
    def wrapper(*args, **kwargs):
        return test_func(*args, **kwargs)
    return wrapper


def requires_redis(test_func):
    """Décorateur pour tests nécessitant Redis."""
    def wrapper(*args, **kwargs):
        return test_func(*args, **kwargs)
    return wrapper


def requires_internet(test_func):
    """Décorateur pour tests nécessitant internet."""
    def wrapper(*args, **kwargs):
        return test_func(*args, **kwargs)
    return wrapper


# ═════════════════════════════════════════════════════════════════════
# SECTION 10: UTILITIES GÉNÉRALES
# ═════════════════════════════════════════════════════════════════════

class TestUtils:
    """Utilitaires de test généraux."""

    @staticmethod
    def compare_dicts_ignore_keys(dict1: Dict, dict2: Dict, ignore_keys: list) -> bool:
        """Compare deux dicts en ignorant certaines clés."""
        for key in ignore_keys:
            dict1.pop(key, None)
            dict2.pop(key, None)
        return dict1 == dict2

    @staticmethod
    def mock_async_func(return_value: Any = None):
        """Crée une fonction async mockée."""
        async def async_func(*args, **kwargs):
            return return_value
        return AsyncMock(side_effect=async_func)

    @staticmethod
    def create_multiline_string(*lines) -> str:
        """Crée une string multiligne pour tests."""
        return "\n".join(lines)

    @staticmethod
    def measure_test_time(test_func):
        """Décorateur pour mesurer temps d'exécution d'un test."""
        def wrapper(*args, **kwargs):
            import time
            start = time.time()
            result = test_func(*args, **kwargs)
            duration = time.time() - start
            print(f"Test '{test_func.__name__}' took {duration:.3f}s")
            return result
        return wrapper
