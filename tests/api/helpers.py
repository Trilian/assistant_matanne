"""
Test Helpers & Utilities for API Tests
════════════════════════════════════════════════════════════════════

Centralisation des patterns réutilisables pour tests API FastAPI.
Évite duplication entre tests/api/*.py

Usage:
    from tests.api.helpers import (
        APITestClient, create_test_request,
        MockedAuthProvider, APIResponseValidator
    )
"""

from unittest.mock import Mock, MagicMock, patch, AsyncMock
from contextlib import contextmanager
from typing import Any, Dict, Optional, Generator, Type
from dataclasses import dataclass
import pytest
from fastapi.testclient import TestClient
from httpx import Response


# ═════════════════════════════════════════════════════════════════════
# SECTION 1: TEST CLIENT BUILDERS
# ═════════════════════════════════════════════════════════════════════

class APITestClientBuilder:
    """Builder pour créer des clients test FastAPI configurés."""

    @staticmethod
    def create_test_client(app) -> TestClient:
        """Crée un client test standard."""
        return TestClient(app)

    @staticmethod
    def create_authenticated_client(app, token: str = "test-token") -> TestClient:
        """Crée un client test avec authentification."""
        client = TestClient(app)
        client.headers = {"Authorization": f"Bearer {token}"}
        return client

    @staticmethod
    def create_client_with_headers(app, headers: Dict[str, str]) -> TestClient:
        """Crée un client test avec headers personnalisés."""
        client = TestClient(app)
        client.headers.update(headers)
        return client

    @staticmethod
    def create_client_with_cookies(app, cookies: Dict[str, str]) -> TestClient:
        """Crée un client test avec cookies."""
        client = TestClient(app)
        client.cookies.update(cookies)
        return client


# ═════════════════════════════════════════════════════════════════════
# SECTION 2: REQUEST/RESPONSE BUILDERS
# ═════════════════════════════════════════════════════════════════════

class APIRequestBuilder:
    """Builder pour créer requêtes test cohérentes."""

    @staticmethod
    def create_test_request(
        method: str = "GET",
        path: str = "/",
        **kwargs
    ) -> Dict[str, Any]:
        """Crée une requête test."""
        return {
            "method": method,
            "path": path,
            **kwargs
        }

    @staticmethod
    def create_get_request(path: str, params: Optional[Dict] = None) -> Dict:
        """Crée une requête GET."""
        return {
            "method": "GET",
            "path": path,
            "params": params or {},
        }

    @staticmethod
    def create_post_request(path: str, json: Optional[Dict] = None) -> Dict:
        """Crée une requête POST."""
        return {
            "method": "POST",
            "path": path,
            "json": json or {},
        }

    @staticmethod
    def create_put_request(path: str, json: Optional[Dict] = None) -> Dict:
        """Crée une requête PUT."""
        return {
            "method": "PUT",
            "path": path,
            "json": json or {},
        }

    @staticmethod
    def create_delete_request(path: str) -> Dict:
        """Crée une requête DELETE."""
        return {
            "method": "DELETE",
            "path": path,
        }

    @staticmethod
    def create_patch_request(path: str, json: Optional[Dict] = None) -> Dict:
        """Crée une requête PATCH."""
        return {
            "method": "PATCH",
            "path": path,
            "json": json or {},
        }


@dataclass
class APIResponse:
    """Wrapper pour response API avec helpers."""
    response: Response

    @property
    def status_code(self) -> int:
        return self.response.status_code

    @property
    def json(self) -> Dict:
        return self.response.json()

    @property
    def text(self) -> str:
        return self.response.text

    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    def is_client_error(self) -> bool:
        return 400 <= self.status_code < 500

    def is_server_error(self) -> bool:
        return 500 <= self.status_code < 600


# ═════════════════════════════════════════════════════════════════════
# SECTION 3: MOCK BUILDERS
# ═════════════════════════════════════════════════════════════════════

class APIMockBuilder:
    """Builder pour créer mocks API cohérents."""

    @staticmethod
    def create_auth_mock(token: str = "test-token", user_id: str = "123") -> Mock:
        """Crée un mock authentification."""
        auth = Mock()
        auth.verify_token = Mock(return_value=token)
        auth.get_current_user = Mock(return_value={"user_id": user_id})
        auth.is_authenticated = Mock(return_value=True)
        return auth

    @staticmethod
    def create_rate_limiter_mock() -> Mock:
        """Crée un mock rate limiter."""
        limiter = Mock()
        limiter.is_rate_limited = Mock(return_value=False)
        limiter.check_limit = Mock(return_value=True)
        limiter.get_remaining = Mock(return_value=100)
        limiter.reset = Mock()
        return limiter

    @staticmethod
    def create_cache_mock() -> Mock:
        """Crée un mock cache."""
        cache = Mock()
        cache.get = Mock(return_value=None)
        cache.set = Mock(return_value=True)
        cache.delete = Mock(return_value=True)
        cache.clear = Mock(return_value=True)
        return cache

    @staticmethod
    def create_db_mock() -> Mock:
        """Crée un mock BD."""
        db = Mock()
        db.query = Mock(return_value=Mock(all=Mock(return_value=[])))
        db.add = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        db.close = Mock()
        return db


# ═════════════════════════════════════════════════════════════════════
# SECTION 4: CONTEXT MANAGERS
# ═════════════════════════════════════════════════════════════════════

@contextmanager
def mock_auth_context(token: str = "test-token", user_id: str = "123"):
    """Context manager pour mock authentification."""
    auth = APIMockBuilder.create_auth_mock(token, user_id)
    with patch("src.api.auth.get_current_user", return_value={"user_id": user_id}):
        yield auth


@contextmanager
def mock_rate_limiter_context(rate_limited: bool = False):
    """Context manager pour mock rate limiter."""
    limiter = APIMockBuilder.create_rate_limiter_mock()
    limiter.is_rate_limited.return_value = rate_limited
    with patch("src.api.rate_limiting.RateLimiter", return_value=limiter):
        yield limiter


@contextmanager
def mock_cache_context(cached_data: Optional[Dict] = None):
    """Context manager pour mock cache."""
    cache = APIMockBuilder.create_cache_mock()
    if cached_data:
        cache.get.return_value = cached_data
    with patch("src.api.cache.Cache", return_value=cache):
        yield cache


@contextmanager
def mock_db_context(db_data: Optional[list] = None):
    """Context manager pour mock BD."""
    db = APIMockBuilder.create_db_mock()
    if db_data:
        db.query.return_value.all.return_value = db_data
    with patch("src.api.database.get_db", return_value=db):
        yield db


# ═════════════════════════════════════════════════════════════════════
# SECTION 5: TEST DATA FACTORIES
# ═════════════════════════════════════════════════════════════════════

def create_api_test_data(data_type: str, **kwargs) -> Any:
    """Factory pour créer données test API."""
    factories = {
        'user': lambda: {
            'id': kwargs.get('id', 'user-123'),
            'name': kwargs.get('name', 'Test User'),
            'email': kwargs.get('email', 'test@example.com'),
            'role': kwargs.get('role', 'user'),
            **kwargs.get('extra', {})
        },
        'recipe': lambda: {
            'id': kwargs.get('id', 1),
            'nom': kwargs.get('nom', 'Test Recipe'),
            'description': kwargs.get('description', 'Test description'),
            'portions': kwargs.get('portions', 4),
            'temps_preparation': kwargs.get('temps_preparation', 15),
            'temps_cuisson': kwargs.get('temps_cuisson', 30),
            **kwargs.get('extra', {})
        },
        'inventory_item': lambda: {
            'id': kwargs.get('id', 1),
            'nom': kwargs.get('nom', 'Ingredient'),
            'quantite': kwargs.get('quantite', 100),
            'unite': kwargs.get('unite', 'g'),
            'categorie': kwargs.get('categorie', 'fruits'),
            **kwargs.get('extra', {})
        },
        'planning': lambda: {
            'id': kwargs.get('id', 1),
            'titre': kwargs.get('titre', 'Test Plan'),
            'date': kwargs.get('date', '2026-01-30'),
            'description': kwargs.get('description', ''),
            **kwargs.get('extra', {})
        },
        'api_token': lambda: {
            'token': kwargs.get('token', 'test-token-123'),
            'user_id': kwargs.get('user_id', 'user-123'),
            'expires_at': kwargs.get('expires_at', '2099-12-31'),
        }
    }

    if data_type not in factories:
        raise ValueError(f"Unknown data_type: {data_type}")

    return factories[data_type]()


# ═════════════════════════════════════════════════════════════════════
# SECTION 6: RESPONSE VALIDATORS
# ═════════════════════════════════════════════════════════════════════

class APIResponseValidator:
    """Validators pour réponses API."""

    @staticmethod
    def assert_status_code(response: Response, expected: int) -> None:
        """Vérifie le status code."""
        assert response.status_code == expected, \
            f"Expected {expected}, got {response.status_code}: {response.text}"

    @staticmethod
    def assert_success(response: Response) -> None:
        """Vérifie réponse success (200-299)."""
        assert 200 <= response.status_code < 300, \
            f"Expected success, got {response.status_code}: {response.text}"

    @staticmethod
    def assert_client_error(response: Response) -> None:
        """Vérifie réponse client error (400-499)."""
        assert 400 <= response.status_code < 500, \
            f"Expected client error, got {response.status_code}"

    @staticmethod
    def assert_server_error(response: Response) -> None:
        """Vérifie réponse server error (500-599)."""
        assert 500 <= response.status_code < 600, \
            f"Expected server error, got {response.status_code}"

    @staticmethod
    def assert_json_response(response: Response, expected_keys: list) -> None:
        """Vérifie structure JSON response."""
        data = response.json()
        assert isinstance(data, dict), "Response is not JSON dict"
        missing = set(expected_keys) - set(data.keys())
        assert not missing, f"Missing keys in response: {missing}"

    @staticmethod
    def assert_has_error(response: Response, error_type: str) -> None:
        """Vérifie qu'une erreur est présente."""
        data = response.json()
        assert "error" in data or "detail" in data, "No error in response"

    @staticmethod
    def assert_pagination(response: Response) -> None:
        """Vérifie structure pagination."""
        data = response.json()
        assert "items" in data, "Missing 'items' in pagination"
        assert "total" in data or "count" in data, "Missing count in pagination"


# ═════════════════════════════════════════════════════════════════════
# SECTION 7: PARAMETRIZE DATA SETS
# ═════════════════════════════════════════════════════════════════════

class APIParametrizeData:
    """Données pour pytest.mark.parametrize courants."""

    # Status codes
    SUCCESS_CODES = [200, 201, 202, 204]
    CLIENT_ERROR_CODES = [400, 401, 403, 404, 409]
    SERVER_ERROR_CODES = [500, 502, 503]

    # HTTP Methods
    HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]

    # Content types
    CONTENT_TYPES = [
        "application/json",
        "application/x-www-form-urlencoded",
        "multipart/form-data",
    ]

    # Invalid inputs
    INVALID_INPUTS = [
        "",
        None,
        "   ",
        "<script>alert('xss')</script>",
        "'; DROP TABLE users; --",
        {"$ne": None},  # NoSQL injection
    ]

    # Valid IDs
    VALID_IDS = ["123", "user-abc-def", "550e8400-e29b-41d4-a716-446655440000"]

    # Invalid IDs
    INVALID_IDS = ["", None, "   ", "invalid@#$%"]


# ═════════════════════════════════════════════════════════════════════
# SECTION 8: PYTEST FIXTURES
# ═════════════════════════════════════════════════════════════════════

@pytest.fixture
def api_client(app):
    """Fixture client test API."""
    return APITestClientBuilder.create_test_client(app)


@pytest.fixture
def authenticated_api_client(app):
    """Fixture client test API authentifié."""
    return APITestClientBuilder.create_authenticated_client(app)


@pytest.fixture
def mock_auth():
    """Fixture mock authentification."""
    return APIMockBuilder.create_auth_mock()


@pytest.fixture
def mock_rate_limiter():
    """Fixture mock rate limiter."""
    return APIMockBuilder.create_rate_limiter_mock()


@pytest.fixture
def mock_cache():
    """Fixture mock cache."""
    return APIMockBuilder.create_cache_mock()


@pytest.fixture
def mock_db():
    """Fixture mock BD."""
    return APIMockBuilder.create_db_mock()


@pytest.fixture
def test_user_data():
    """Fixture données utilisateur test."""
    return create_api_test_data('user')


@pytest.fixture
def test_recipe_data():
    """Fixture données recette test."""
    return create_api_test_data('recipe')


@pytest.fixture
def test_inventory_data():
    """Fixture données inventaire test."""
    return create_api_test_data('inventory_item')


@pytest.fixture
def test_planning_data():
    """Fixture données planning test."""
    return create_api_test_data('planning')


@pytest.fixture
def test_token_data():
    """Fixture données token test."""
    return create_api_test_data('api_token')


# ═════════════════════════════════════════════════════════════════════
# SECTION 9: COMMON TEST PATTERNS
# ═════════════════════════════════════════════════════════════════════

class APITestPatterns:
    """Patterns répétés dans tests API."""

    @staticmethod
    def setup_authenticated_request():
        """Setup requête authentifiée."""
        return {
            "headers": {"Authorization": "Bearer test-token"},
            "json": {}
        }

    @staticmethod
    def setup_rate_limited_scenario():
        """Setup scénario rate limited."""
        return {
            "request_count": 101,
            "limit": 100,
            "window": "minute",
        }

    @staticmethod
    def assert_success_response(response: Response, status_code: int = 200):
        """Pattern: vérifier réponse success."""
        APIResponseValidator.assert_status_code(response, status_code)
        APIResponseValidator.assert_success(response)

    @staticmethod
    def assert_error_response(response: Response, status_code: int = 400):
        """Pattern: vérifier réponse erreur."""
        APIResponseValidator.assert_status_code(response, status_code)
        APIResponseValidator.assert_has_error(response, "error")


# ═════════════════════════════════════════════════════════════════════
# SECTION 10: UTILITIES
# ═════════════════════════════════════════════════════════════════════

class APITestUtils:
    """Utilitaires généraux pour tests API."""

    @staticmethod
    def get_auth_header(token: str = "test-token") -> Dict[str, str]:
        """Génère header authentification."""
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def get_json_header() -> Dict[str, str]:
        """Génère header JSON."""
        return {"Content-Type": "application/json"}

    @staticmethod
    def get_request_id() -> str:
        """Génère request ID unique."""
        import uuid
        return str(uuid.uuid4())

    @staticmethod
    def build_url(path: str, params: Optional[Dict] = None) -> str:
        """Construit URL avec paramètres."""
        if not params:
            return path
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{path}?{query_string}"

    @staticmethod
    def mock_async_function(return_value: Any = None):
        """Crée une fonction async mockée."""
        async def async_func(*args, **kwargs):
            return return_value
        return AsyncMock(side_effect=async_func)
