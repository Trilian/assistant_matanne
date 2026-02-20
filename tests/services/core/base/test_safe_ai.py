"""Tests pour l'API safe de BaseAIService et health_check.

Vérifie que les méthodes safe_* retournent des Result au lieu de None.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from src.services.core.base.result import (
    ErrorCode,
    Failure,
    Success,
)

# ═══════════════════════════════════════════════════════════
# MODÈLES DE TEST
# ═══════════════════════════════════════════════════════════


class FakeResponse(BaseModel):
    """Modèle Pydantic pour tests de parsing."""

    nom: str
    score: float = 0.0


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_client():
    """Client IA mocké."""
    client = MagicMock()
    client.appeler = AsyncMock(return_value="réponse test")
    return client


@pytest.fixture
def ai_service(mock_client):
    """BaseAIService avec client mocké."""
    from src.services.core.base.ai_service import BaseAIService

    with (
        patch("src.services.core.base.ai_service.RateLimitIA") as mock_rl,
        patch("src.services.core.base.ai_service.CacheIA") as mock_cache,
    ):
        mock_rl.peut_appeler.return_value = (True, "")
        mock_rl.enregistrer_appel.return_value = None
        mock_cache.obtenir.return_value = None  # pas de cache
        mock_cache.definir.return_value = None
        mock_cache.obtenir_statistiques.return_value = {}
        mock_cache.invalider_tout.return_value = None

        svc = BaseAIService(
            client=mock_client,
            cache_prefix="test",
            service_name="test_service",
        )
        # Store mocks pour les assertions
        svc._mock_rate_limit = mock_rl
        svc._mock_cache = mock_cache
        yield svc


# ═══════════════════════════════════════════════════════════
# TESTS safe_call_with_cache
# ═══════════════════════════════════════════════════════════


class TestSafeCallWithCache:
    """Tests pour safe_call_with_cache."""

    @pytest.mark.asyncio
    async def test_success(self, ai_service):
        """Retourne Success[str] si appel réussi."""
        result = await ai_service.safe_call_with_cache("prompt test")

        assert isinstance(result, Success)
        assert isinstance(result.value, str)

    @pytest.mark.asyncio
    async def test_failure_when_client_none(self):
        """Retourne Failure AI_UNAVAILABLE si client=None."""
        from src.services.core.base.ai_service import BaseAIService

        with (
            patch("src.services.core.base.ai_service.RateLimitIA"),
            patch("src.services.core.base.ai_service.CacheIA") as mock_cache,
        ):
            mock_cache.obtenir.return_value = None
            svc = BaseAIService(client=None, service_name="test")

            result = await svc.safe_call_with_cache("prompt")

            assert isinstance(result, Failure)
            assert result.error.code == ErrorCode.AI_UNAVAILABLE

    @pytest.mark.asyncio
    async def test_failure_on_rate_limit(self, ai_service):
        """Retourne Failure RATE_LIMITED si quota dépassé."""
        from src.core.errors_base import ErreurLimiteDebit

        ai_service._mock_rate_limit.peut_appeler.return_value = (False, "Quota atteint")

        # call_with_cache va lever ErreurLimiteDebit
        result = await ai_service.safe_call_with_cache("prompt")

        assert isinstance(result, Failure)
        assert result.error.code == ErrorCode.RATE_LIMITED

    @pytest.mark.asyncio
    async def test_source_is_service_name(self, ai_service):
        """La source dans ErrorInfo est le service_name."""
        ai_service.client = None  # Force erreur

        result = await ai_service.safe_call_with_cache("p")

        assert result.error.source == "test_service"


# ═══════════════════════════════════════════════════════════
# TESTS safe_call_with_parsing
# ═══════════════════════════════════════════════════════════


class TestSafeCallWithParsing:
    """Tests pour safe_call_with_parsing."""

    @pytest.mark.asyncio
    async def test_success_when_parsed(self, ai_service, mock_client):
        """Retourne Success[BaseModel] si parsing OK."""
        mock_client.appeler = AsyncMock(return_value='{"nom": "Test", "score": 9.5}')

        with patch(
            "src.services.core.base.ai_service.AnalyseurIA.analyser",
            return_value=FakeResponse(nom="Test", score=9.5),
        ):
            result = await ai_service.safe_call_with_parsing("prompt", FakeResponse)

            assert isinstance(result, Success)
            assert result.value.nom == "Test"
            assert result.value.score == 9.5

    @pytest.mark.asyncio
    async def test_failure_when_parse_fails(self, ai_service, mock_client):
        """Retourne Failure PARSING_ERROR si parsing échoue."""
        mock_client.appeler = AsyncMock(return_value="invalid json")

        # Simuler que call_with_parsing retourne None
        ai_service.call_with_parsing = AsyncMock(return_value=None)

        result = await ai_service.safe_call_with_parsing("prompt", FakeResponse)

        assert isinstance(result, Failure)
        assert result.error.code == ErrorCode.PARSING_ERROR
        assert "FakeResponse" in result.error.message


# ═══════════════════════════════════════════════════════════
# TESTS safe_call_with_list_parsing
# ═══════════════════════════════════════════════════════════


class TestSafeCallWithListParsing:
    """Tests pour safe_call_with_list_parsing."""

    @pytest.mark.asyncio
    async def test_success_with_items(self, ai_service):
        """Retourne Success[list] si parsing liste OK."""
        items = [FakeResponse(nom="A"), FakeResponse(nom="B")]
        ai_service.call_with_list_parsing = AsyncMock(return_value=items)

        result = await ai_service.safe_call_with_list_parsing("prompt", FakeResponse)

        assert isinstance(result, Success)
        assert len(result.value) == 2

    @pytest.mark.asyncio
    async def test_success_empty_list(self, ai_service):
        """Retourne Success([]) si aucun item."""
        ai_service.call_with_list_parsing = AsyncMock(return_value=[])

        result = await ai_service.safe_call_with_list_parsing("prompt", FakeResponse)

        assert isinstance(result, Success)
        assert result.value == []


# ═══════════════════════════════════════════════════════════
# TESTS safe_call_with_json_parsing
# ═══════════════════════════════════════════════════════════


class TestSafeCallWithJsonParsing:
    """Tests pour safe_call_with_json_parsing."""

    @pytest.mark.asyncio
    async def test_success_when_parsed(self, ai_service):
        """Retourne Success si JSON parsing OK."""
        ai_service.call_with_json_parsing = AsyncMock(
            return_value=FakeResponse(nom="JSON", score=1.0)
        )

        result = await ai_service.safe_call_with_json_parsing("prompt", FakeResponse)

        assert isinstance(result, Success)
        assert result.value.nom == "JSON"

    @pytest.mark.asyncio
    async def test_failure_when_none(self, ai_service):
        """Retourne Failure PARSING_ERROR si retourne None."""
        ai_service.call_with_json_parsing = AsyncMock(return_value=None)

        result = await ai_service.safe_call_with_json_parsing("prompt", FakeResponse)

        assert isinstance(result, Failure)
        assert result.error.code == ErrorCode.PARSING_ERROR


# ═══════════════════════════════════════════════════════════
# TESTS health_check BaseAIService
# ═══════════════════════════════════════════════════════════


class TestAIHealthCheck:
    """Tests pour health_check de BaseAIService."""

    def test_healthy_when_all_ok(self, ai_service):
        """health_check retourne HEALTHY si client + rate limit OK."""
        from src.services.core.base.protocols import ServiceStatus

        health = ai_service.health_check()

        assert health.status == ServiceStatus.HEALTHY
        assert "opérationnel" in health.message
        assert health.latency_ms >= 0
        assert "AI:" in health.service_name

    def test_unhealthy_when_no_client(self):
        """health_check retourne UNHEALTHY si pas de client."""
        from src.services.core.base.ai_service import BaseAIService
        from src.services.core.base.protocols import ServiceStatus

        with (
            patch("src.services.core.base.ai_service.RateLimitIA") as mock_rl,
            patch("src.services.core.base.ai_service.CacheIA") as mock_cache,
        ):
            mock_rl.peut_appeler.return_value = (True, "")
            mock_rl.obtenir_statistiques.return_value = {}
            mock_cache.obtenir_statistiques.return_value = {}

            svc = BaseAIService(client=None, service_name="no_client")
            health = svc.health_check()

            assert health.status == ServiceStatus.UNHEALTHY
            assert "indisponible" in health.message

    def test_degraded_when_rate_limited(self, ai_service):
        """health_check retourne DEGRADED si rate limité."""
        from src.services.core.base.protocols import ServiceStatus

        ai_service._mock_rate_limit.peut_appeler.return_value = (False, "Quota 100/100")

        health = ai_service.health_check()

        assert health.status == ServiceStatus.DEGRADED
        assert "limité" in health.message.lower()

    def test_health_includes_stats(self, ai_service):
        """health_check inclut les stats rate limit et cache."""
        health = ai_service.health_check()

        assert "rate_limit_stats" in health.details
        assert "cache_stats" in health.details
        assert "client_available" in health.details
