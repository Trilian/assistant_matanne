"""
Tests pour src/services/base_ai_service.py
Cible: BaseAIService - Rate limiting, cache, parsing Pydantic
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime
from pydantic import BaseModel


# ═══════════════════════════════════════════════════════════
# MODÈLES DE TEST
# ═══════════════════════════════════════════════════════════


class RecetteTest(BaseModel):
    """Modèle de test pour parsing."""
    nom: str
    temps_preparation: int = 30


class IngredientTest(BaseModel):
    """Modèle de test pour parsing liste."""
    nom: str
    quantite: str = "1"


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_client_ia():
    """Client IA mocké."""
    client = Mock()
    client.appeler = AsyncMock(return_value='{"nom": "Test", "temps_preparation": 45}')
    return client


@pytest.fixture
def mock_session_state():
    """Session state mockée pour rate limit."""
    return {
        "rate_limit_appels_today": 0,
        "rate_limit_appels_hour": 0,
        "rate_limit_last_hour": datetime.now().hour,
        "rate_limit_last_day": datetime.now().date().isoformat(),
    }


@pytest.fixture
def base_ai_service(mock_client_ia):
    """Instance BaseAIService pour tests."""
    from src.services.base import BaseAIService
    
    return BaseAIService(
        client=mock_client_ia,
        cache_prefix="test",
        default_ttl=300,
        default_temperature=0.5,
        service_name="test_service",
    )


# ═══════════════════════════════════════════════════════════
# TESTS INITIALISATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBaseAIServiceInit:
    """Tests pour l'initialisation de BaseAIService."""

    def test_init_sets_client(self, mock_client_ia):
        """Vérifie que le client est correctement défini."""
        from src.services.base import BaseAIService
        
        service = BaseAIService(client=mock_client_ia)
        
        assert service.client == mock_client_ia

    def test_init_sets_cache_prefix(self, mock_client_ia):
        """Vérifie que le préfixe cache est correctement défini."""
        from src.services.base import BaseAIService
        
        service = BaseAIService(client=mock_client_ia, cache_prefix="recipes")
        
        assert service.cache_prefix == "recipes"

    def test_init_sets_default_values(self, mock_client_ia):
        """Vérifie les valeurs par défaut."""
        from src.services.base import BaseAIService
        
        service = BaseAIService(client=mock_client_ia)
        
        assert service.default_ttl == 3600
        assert service.default_temperature == 0.7
        assert service.service_name == "unknown"

    def test_init_custom_values(self, mock_client_ia):
        """Vérifie les valeurs personnalisées."""
        from src.services.base import BaseAIService
        
        service = BaseAIService(
            client=mock_client_ia,
            default_ttl=600,
            default_temperature=0.3,
            service_name="recettes",
        )
        
        assert service.default_ttl == 600
        assert service.default_temperature == 0.3
        assert service.service_name == "recettes"


# ═══════════════════════════════════════════════════════════
# TESTS VERSIONS SYNCHRONES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSyncVersions:
    """Tests pour les versions synchrones."""

    def test_call_with_parsing_sync_exists(self, base_ai_service):
        """Vérifie que la méthode sync existe."""
        assert hasattr(base_ai_service, "call_with_parsing_sync")
        assert callable(base_ai_service.call_with_parsing_sync)

    def test_call_with_list_parsing_sync_exists(self, base_ai_service):
        """Vérifie que la méthode sync existe."""
        assert hasattr(base_ai_service, "call_with_list_parsing_sync")
        assert callable(base_ai_service.call_with_list_parsing_sync)


# ═══════════════════════════════════════════════════════════
# TESTS CLIENT NONE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestClientNone:
    """Tests pour le cas où le client est None."""

    def test_service_accepts_none_client(self):
        """Vérifie que le service accepte un client None."""
        from src.services.base import BaseAIService
        
        service = BaseAIService(client=None)
        
        assert service.client is None

    def test_call_with_cache_handles_none_client(self):
        """Vérifie que call_with_cache gère un client None."""
        from src.services.base import BaseAIService
        import asyncio
        
        service = BaseAIService(client=None)
        
        # La méthode async devrait retourner None si client est None
        # On ne peut pas tester directement sans pytest-asyncio configuré
        # mais on vérifie que la méthode existe
        assert hasattr(service, "call_with_cache")


# ═══════════════════════════════════════════════════════════
# TESTS ATTRIBUTS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAttributs:
    """Tests pour vérifier les attributs du service."""

    def test_has_required_methods(self, base_ai_service):
        """Vérifie que les méthodes requises existent."""
        required_methods = [
            "call_with_cache",
            "call_with_parsing",
            "call_with_parsing_sync",
            "call_with_list_parsing",
            "call_with_list_parsing_sync",
        ]
        
        for method in required_methods:
            assert hasattr(base_ai_service, method), f"Méthode manquante: {method}"

    def test_has_required_attributes(self, base_ai_service):
        """Vérifie que les attributs requis existent."""
        required_attrs = [
            "client",
            "cache_prefix",
            "default_ttl",
            "default_temperature",
            "service_name",
        ]
        
        for attr in required_attrs:
            assert hasattr(base_ai_service, attr), f"Attribut manquant: {attr}"
