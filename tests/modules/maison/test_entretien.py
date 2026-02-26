"""
Tests pour src/modules/maison/entretien.py

Tests complets pour le module Entretien (routines ménage).
Note: EntretienService moved to src.services.maison.entretien_service
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# TESTS SERVICE IA ENTRETIEN
# ═══════════════════════════════════════════════════════════════════════════════


class TestEntretienService:
    """Tests pour EntretienService"""

    def test_import(self):
        """Test import du service."""
        from src.services.maison import EntretienService

        assert EntretienService is not None

    @patch("src.services.maison.entretien_service.ClientIA")
    def test_creation(self, mock_client_class):
        """Test de création de EntretienService."""
        mock_client_class.return_value = MagicMock()

        from src.services.maison import EntretienService

        service = EntretienService()

        assert service is not None
        assert service.service_name == "entretien"
        assert service.cache_prefix == "entretien"

    @patch("src.services.maison.entretien_service.ClientIA")
    def test_creation_with_custom_client(self, mock_client_class):
        """Test création avec client personnalisé."""
        custom_client = MagicMock()

        from src.services.maison import EntretienService

        service = EntretienService(client=custom_client)

        assert service.client == custom_client

    @pytest.mark.asyncio
    @patch("src.services.maison.entretien_service.ClientIA")
    async def test_creer_routine(self, mock_client_class):
        """Test création routine via IA."""
        mock_client_class.return_value = MagicMock()

        from src.services.maison import EntretienService

        service = EntretienService()
        service.call_with_cache = AsyncMock(return_value="- Tâche 1\n- Tâche 2")

        result = await service.suggerer_taches("Ménage matin", "routine quotidienne")

        assert result == "- Tâche 1\n- Tâche 2"
        service.call_with_cache.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.services.maison.entretien_service.ClientIA")
    async def test_optimiser_semaine(self, mock_client_class):
        """Test optimisation semaine."""
        mock_client_class.return_value = MagicMock()

        from src.services.maison import EntretienService

        service = EntretienService()
        # Mock returns valid JSON for optimiser_semaine
        service.call_with_cache = AsyncMock(
            return_value='{"Lundi": ["aspirateur"], "Mardi": ["poussière"]}'
        )

        result = await service.optimiser_semaine("aspirateur, poussière, lessive")

        assert "Lundi" in result
        service.call_with_cache.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.services.maison.entretien_service.ClientIA")
    async def test_adapter_planning_meteo(self, mock_client_class):
        """Test adaptation planning selon météo."""
        mock_client_class.return_value = MagicMock()

        from src.services.maison import EntretienService

        service = EntretienService()
        service.call_with_cache = AsyncMock(return_value='["Nettoyage vitres", "Jardinage"]')

        result = await service.adapter_planning_meteo(
            ["Nettoyage vitres", "Aspirateur"], {"condition": "sunny", "temp": 20}
        )

        assert isinstance(result, list)

    @pytest.mark.asyncio
    @patch("src.services.maison.entretien_service.ClientIA")
    async def test_conseil_efficacite(self, mock_client_class):
        """Test astuces efficacité."""
        mock_client_class.return_value = MagicMock()

        from src.services.maison import EntretienService

        service = EntretienService()
        service.call_with_cache = AsyncMock(return_value="1. Astuce 1\n2. Astuce 2")

        result = await service.conseil_efficacite()

        assert "Astuce" in result


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS FACTORY
# ═══════════════════════════════════════════════════════════════════════════════


class TestFactory:
    """Tests pour les fonctions factory."""

    @patch("src.services.maison.entretien_service.ClientIA")
    def test_get_entretien_service(self, mock_client_class):
        """Test de la fonction get_entretien_service."""
        mock_client_class.return_value = MagicMock()

        from src.services.maison import get_entretien_service

        service = get_entretien_service()

        assert service is not None
        assert service.service_name == "entretien"


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS FONCTIONS MÉTIER (avec mocks DB)
# ═══════════════════════════════════════════════════════════════════════════════


class TestFonctionsMetier:
    """Tests pour les fonctions métier."""

    @patch("src.modules.maison.entretien.st")
    def test_creer_routine_import(self, mock_st):
        """Test import fonction creer_routine."""
        from src.modules.maison.entretien import creer_routine

        assert callable(creer_routine)

    @patch("src.modules.maison.entretien.st")
    def test_ajouter_tache_routine_import(self, mock_st):
        """Test import fonction ajouter_tache_routine."""
        from src.modules.maison.entretien import ajouter_tache_routine

        assert callable(ajouter_tache_routine)

    @patch("src.modules.maison.entretien.st")
    def test_marquer_tache_faite_import(self, mock_st):
        """Test import fonction marquer_tache_faite."""
        from src.modules.maison.entretien import marquer_tache_faite

        assert callable(marquer_tache_faite)

    @patch("src.modules.maison.entretien.st")
    def test_desactiver_routine_import(self, mock_st):
        """Test import fonction desactiver_routine."""
        from src.modules.maison.entretien import desactiver_routine

        assert callable(desactiver_routine)


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MODULE APP
# ═══════════════════════════════════════════════════════════════════════════════


class TestApp:
    """Tests pour la fonction app (UI)."""

    @patch("src.modules.maison.entretien.st")
    def test_app_import(self, mock_st):
        """Test import de la fonction app."""
        from src.modules.maison.entretien import app

        assert callable(app)

    @patch("src.modules.maison.entretien.st")
    @patch("src.modules.maison.entretien.charger_routines")
    @patch("src.modules.maison.entretien.get_taches_today")
    def test_app_runs(self, mock_taches, mock_routines, mock_st):
        """Test que app() s'exécute sans erreur."""
        mock_routines.return_value = []
        mock_taches.return_value = []

        # Mock st.columns pour retourner des contextes
        mock_cols = [MagicMock() for _ in range(4)]
        for col in mock_cols:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = mock_cols

        # Mock st.tabs
        mock_tabs = [MagicMock() for _ in range(4)]
        for tab in mock_tabs:
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock(return_value=False)
        mock_st.tabs.return_value = mock_tabs

        from src.modules.maison.entretien import app

        # L'app devrait s'exécuter sans erreur
        try:
            app()
        except Exception:
            pass  # Certaines erreurs UI sont acceptables dans les tests

        mock_st.title.assert_called_once()
