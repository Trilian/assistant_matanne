"""
Tests pour src/services/famille/weekend_ai.py

Tests complets pour le service IA Weekend.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestWeekendAIService:
    """Tests pour WeekendAIService"""

    def test_import(self):
        """Test import du service."""
        from src.services.famille.weekend_ai import WeekendAIService

        assert WeekendAIService is not None

    @patch("src.services.famille.weekend_ai.obtenir_client_ia")
    def test_creation(self, mock_factory):
        """Test de création de WeekendAIService."""
        mock_factory.return_value = MagicMock()

        from src.services.famille.weekend_ai import WeekendAIService

        service = WeekendAIService()

        assert service is not None
        assert service.service_name == "weekend_ai"
        assert service.cache_prefix == "weekend"

    @patch("src.services.famille.weekend_ai.obtenir_client_ia")
    def test_service_attributes(self, mock_factory):
        """Test des attributs du service."""
        mock_factory.return_value = MagicMock()

        from src.services.famille.weekend_ai import WeekendAIService

        service = WeekendAIService()

        assert hasattr(service, "call_with_cache")
        assert service.default_ttl == 3600

    @pytest.mark.asyncio
    @patch("src.services.famille.weekend_ai.obtenir_client_ia")
    async def test_suggerer_activites(self, mock_factory):
        """Test suggestion d'activités weekend."""
        mock_factory.return_value = MagicMock()

        from src.services.famille.weekend_ai import WeekendAIService

        service = WeekendAIService()
        service.call_with_cache = AsyncMock(return_value="Activité suggérée")

        result = await service.suggerer_activites(
            meteo="ensoleillé", age_enfant_mois=24, budget=100, region="Paris"
        )

        assert result == "Activité suggérée"
        service.call_with_cache.assert_called_once()
        call_args = service.call_with_cache.call_args
        assert "24" in call_args.kwargs["prompt"]
        assert "100" in call_args.kwargs["prompt"]

    @pytest.mark.asyncio
    @patch("src.services.famille.weekend_ai.obtenir_client_ia")
    async def test_suggerer_activites_params_default(self, mock_factory):
        """Test suggestion avec paramètres par défaut."""
        mock_factory.return_value = MagicMock()

        from src.services.famille.weekend_ai import WeekendAIService

        service = WeekendAIService()
        service.call_with_cache = AsyncMock(return_value="Suggestions")

        result = await service.suggerer_activites()

        assert result == "Suggestions"
        call_args = service.call_with_cache.call_args
        assert "19" in call_args.kwargs["prompt"]  # age_enfant_mois default
        assert "50" in call_args.kwargs["prompt"]  # budget default

    @pytest.mark.asyncio
    @patch("src.services.famille.weekend_ai.obtenir_client_ia")
    async def test_details_lieu(self, mock_factory):
        """Test détails d'un lieu."""
        mock_factory.return_value = MagicMock()

        from src.services.famille.weekend_ai import WeekendAIService

        service = WeekendAIService()
        service.call_with_cache = AsyncMock(return_value="Détails du lieu")

        result = await service.details_lieu("Jardin du Luxembourg", "parc")

        assert result == "Détails du lieu"
        service.call_with_cache.assert_called_once()
        call_args = service.call_with_cache.call_args
        assert "Jardin du Luxembourg" in call_args.kwargs["prompt"]
        assert "parc" in call_args.kwargs["prompt"]

    @pytest.mark.asyncio
    @patch("src.services.famille.weekend_ai.obtenir_client_ia")
    async def test_details_lieu_different_type(self, mock_factory):
        """Test détails d'un lieu de type différent."""
        mock_factory.return_value = MagicMock()

        from src.services.famille.weekend_ai import WeekendAIService

        service = WeekendAIService()
        service.call_with_cache = AsyncMock(return_value="Info musée")

        result = await service.details_lieu("Cité des Sciences", "musée")

        assert result == "Info musée"
        call_args = service.call_with_cache.call_args
        assert "Cité des Sciences" in call_args.kwargs["prompt"]
        assert "musée" in call_args.kwargs["prompt"]
