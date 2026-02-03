"""
Pytest Configuration & Fixtures for API Tests
════════════════════════════════════════════════════════════════════

Fixtures partagées pour tous les tests API (tests/api/).
Auto-découverte par pytest.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi.testclient import TestClient


# ═════════════════════════════════════════════════════════════════════
# SECTION 1: PYTEST CONFIGURATION
# ═════════════════════════════════════════════════════════════════════

def pytest_configure(config):
    """Configure pytest avec markers API."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no external deps)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (may use deps)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (require optimization)"
    )
    config.addinivalue_line(
        "markers", "endpoint: Tests for API endpoints"
    )
    config.addinivalue_line(
        "markers", "auth: Tests for authentication"
    )
    config.addinivalue_line(
        "markers", "rate_limit: Tests for rate limiting"
    )
    config.addinivalue_line(
        "markers", "cache: Tests for caching"
    )


# ═════════════════════════════════════════════════════════════════════
# SECTION 2: APP & CLIENT FIXTURES
# ═════════════════════════════════════════════════════════════════════

@pytest.fixture
def app():
    """Fixture app FastAPI pour tests."""
    from src.api.main import app
    return app


@pytest.fixture
def client(app) -> TestClient:
    """Fixture TestClient standard."""
    return TestClient(app)


@pytest.fixture
def authenticated_client(app) -> TestClient:
    """Fixture TestClient avec authentification."""
    client = TestClient(app)
    client.headers = {"Authorization": "Bearer test-token"}
    return client


@pytest.fixture
def client_with_headers(app) -> TestClient:
    """Fixture TestClient avec headers personnalisés."""
    client = TestClient(app)
    client.headers.update({
        "Content-Type": "application/json",
        "X-Request-ID": "test-request-123",
    })
    return client


# ═════════════════════════════════════════════════════════════════════
# SECTION 3: MOCK FIXTURES
# ═════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_auth() -> Mock:
    """Mock authentification."""
    auth = Mock()
    auth.verify_token = Mock(return_value="test-token")
    auth.get_current_user = Mock(return_value={"user_id": "123"})
    auth.is_authenticated = Mock(return_value=True)
    return auth


@pytest.fixture
def mock_rate_limiter() -> Mock:
    """Mock rate limiter."""
    limiter = Mock()
    limiter.is_rate_limited = Mock(return_value=False)
    limiter.check_limit = Mock(return_value=True)
    limiter.get_remaining = Mock(return_value=100)
    return limiter


@pytest.fixture
def mock_cache() -> Mock:
    """Mock cache."""
    cache = Mock()
    cache.get = Mock(return_value=None)
    cache.set = Mock(return_value=True)
    cache.delete = Mock(return_value=True)
    cache.clear = Mock(return_value=True)
    return cache


@pytest.fixture
def mock_db() -> Mock:
    """Mock database."""
    db = Mock()
    db.query = Mock(return_value=Mock(all=Mock(return_value=[])))
    db.add = Mock()
    db.commit = Mock()
    db.rollback = Mock()
    db.close = Mock()
    return db


# ═════════════════════════════════════════════════════════════════════
# SECTION 4: TEST DATA FIXTURES
# ═════════════════════════════════════════════════════════════════════

@pytest.fixture
def test_user() -> dict:
    """Données utilisateur test."""
    return {
        "id": "user-123",
        "name": "Test User",
        "email": "test@example.com",
        "role": "user",
    }


@pytest.fixture
def test_recipe() -> dict:
    """Données recette test."""
    return {
        "id": 1,
        "nom": "Test Recipe",
        "description": "Test description",
        "portions": 4,
        "temps_preparation": 15,
        "temps_cuisson": 30,
        "difficulte": "moyen",
        "categorie": "plats",
    }


@pytest.fixture
def test_recipe_data() -> dict:
    """Données recette test avec données supplémentaires."""
    return {
        "id": 1,
        "nom": "Test Recipe",
        "description": "Test description",
        "portions": 4,
        "temps_preparation": 15,
        "temps_cuisson": 30,
        "difficulte": "moyen",
        "categorie": "plats",
        "ingredients": [{"nom": "tomate", "quantite": 2}],
        "instructions": ["Étape 1", "Étape 2"],
        "tags": ["facile", "rapide"],
    }


@pytest.fixture
def test_inventory_item() -> dict:
    """Données inventaire test."""
    return {
        "id": 1,
        "nom": "Tomate",
        "quantite": 500,
        "unite": "g",
        "categorie": "legumes",
        "date_ajout": "2026-01-29",
    }


@pytest.fixture
def test_planning() -> dict:
    """Données planning test."""
    return {
        "id": 1,
        "titre": "Dîner familial",
        "date": "2026-01-30",
        "description": "Dîner ensemble",
        "participants": ["parent1", "parent2", "enfant"],
    }


@pytest.fixture
def test_token() -> str:
    """Token d'authentification test."""
    return "test-token-xyz-123"


# ═════════════════════════════════════════════════════════════════════
# SECTION 5: CONTEXT MANAGER FIXTURES
# ═════════════════════════════════════════════════════════════════════

@pytest.fixture
def auth_context():
    """Context manager mock authentification."""
    from tests.api.helpers import mock_auth_context
    return mock_auth_context


@pytest.fixture
def rate_limit_context():
    """Context manager mock rate limiter."""
    from tests.api.helpers import mock_rate_limiter_context
    return mock_rate_limiter_context


@pytest.fixture
def cache_context():
    """Context manager mock cache."""
    from tests.api.helpers import mock_cache_context
    return mock_cache_context


@pytest.fixture
def db_context():
    """Context manager mock BD."""
    from tests.api.helpers import mock_db_context
    return mock_db_context


# ═════════════════════════════════════════════════════════════════════
# SECTION 6: HELPER FIXTURES
# ═════════════════════════════════════════════════════════════════════

@pytest.fixture
def api_client_builder():
    """Fixture pour APITestClientBuilder."""
    from tests.api.helpers import APITestClientBuilder
    return APITestClientBuilder


@pytest.fixture
def api_request_builder():
    """Fixture pour APIRequestBuilder."""
    from tests.api.helpers import APIRequestBuilder
    return APIRequestBuilder


@pytest.fixture
def api_mock_builder():
    """Fixture pour APIMockBuilder."""
    from tests.api.helpers import APIMockBuilder
    return APIMockBuilder


@pytest.fixture
def api_response_validator():
    """Fixture pour APIResponseValidator."""
    from tests.api.helpers import APIResponseValidator
    return APIResponseValidator


@pytest.fixture
def api_test_patterns():
    """Fixture pour APITestPatterns."""
    from tests.api.helpers import APITestPatterns
    return APITestPatterns


@pytest.fixture
def api_test_utils():
    """Fixture pour APITestUtils."""
    from tests.api.helpers import APITestUtils
    return APITestUtils


@pytest.fixture
def create_api_test_data():
    """Fixture factory pour créer données test."""
    from tests.api.helpers import create_api_test_data as factory
    return factory


# ═════════════════════════════════════════════════════════════════════
# SECTION 7: CLEANUP FIXTURES
# ═════════════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup automatique après chaque test."""
    yield
    # Cleanup code if needed


@pytest.fixture(autouse=True)
def set_development_environment(monkeypatch):
    """Configure l'environnement en mode développement pour les tests."""
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    yield


@pytest.fixture(autouse=True)
def disable_rate_limiting(monkeypatch):
    """Désactive le rate limiting pour tous les tests API."""
    from unittest.mock import MagicMock, AsyncMock
    
    # Mock le RateLimiter pour qu'il ne bloque jamais
    async def mock_check_rate_limit(*args, **kwargs):
        """Mock check qui ne lève jamais d'exception."""
        return {"remaining": 100, "limit": 1000, "reset": 0}
    
    async def mock_dispatch(self, request, call_next):
        """Mock dispatch qui passe directement au handler."""
        return await call_next(request)
    
    # Patch les méthodes du rate limiter
    try:
        from src.api import rate_limiting
        # Patch check_rate_limit pour ne jamais lever HTTPException
        monkeypatch.setattr(
            rate_limiting.RateLimiter, 
            "check_rate_limit", 
            mock_check_rate_limit
        )
        # Patch le middleware dispatch
        monkeypatch.setattr(
            rate_limiting.RateLimitMiddleware, 
            "dispatch", 
            mock_dispatch
        )
    except (ImportError, AttributeError):
        pass
    
    yield


@pytest.fixture(autouse=True)
def mock_database_for_api(monkeypatch):
    """Mock la base de données pour les tests API."""
    from unittest.mock import MagicMock
    from sqlalchemy.orm import Session
    
    # Créer des mocks pour les recettes
    mock_recette = MagicMock()
    mock_recette.id = 1
    mock_recette.nom = "Test Recipe"
    mock_recette.description = "Description test"
    mock_recette.temps_preparation = 15
    mock_recette.temps_cuisson = 30
    mock_recette.portions = 4
    mock_recette.difficulte = "moyen"
    mock_recette.categorie = "plats"
    mock_recette.created_at = None
    mock_recette.updated_at = None
    
    # Mock query chain
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.count.return_value = 1
    mock_query.all.return_value = [mock_recette]
    mock_query.first.return_value = mock_recette
    
    # Mock session
    mock_session = MagicMock(spec=Session)
    mock_session.query.return_value = mock_query
    mock_session.add = MagicMock()
    mock_session.commit = MagicMock()
    mock_session.rollback = MagicMock()
    mock_session.close = MagicMock()
    mock_session.refresh = MagicMock()
    
    # Mock context manager
    from contextlib import contextmanager
    
    @contextmanager
    def mock_db_context():
        yield mock_session
    
    # Patch get_db_context
    monkeypatch.setattr("src.core.database.obtenir_contexte_db", mock_db_context)
    monkeypatch.setattr("src.core.database.get_db_context", mock_db_context)
    
    yield mock_session


# ═════════════════════════════════════════════════════════════════════
# SECTION 8: PYTEST HOOKS
# ═════════════════════════════════════════════════════════════════════

def pytest_collection_modifyitems(config, items):
    """Ajoute markers par défaut aux tests API."""
    for item in items:
        # Marquer endpoint tests automatiquement
        if "endpoint" in item.nodeid or "test_" in item.nodeid:
            if not any(m.name == "endpoint" for m in item.iter_markers()):
                if not any(m.name in ["unit", "integration"] for m in item.iter_markers()):
                    item.add_marker(pytest.mark.unit)
