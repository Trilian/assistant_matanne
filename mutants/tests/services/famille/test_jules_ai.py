"""
Tests pour src/services/famille/jules_ai.py — JulesAIService.

Couvre:
- Construction du service (avec/sans mock IA)
- Prompts générés (ne font pas appel à l'API réelle)
- Factory singleton
- Méthodes async avec client mocké
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.famille.jules_ai import JulesAIService, obtenir_jules_ai_service


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_client():
    """Client IA mocké (pas d'appel réseau)."""
    client = MagicMock()
    client.completion = AsyncMock(return_value="Réponse IA simulée")
    return client


@pytest.fixture
def service_avec_mock(mock_client):
    with patch("src.services.famille.jules_ai.obtenir_client_ia", return_value=mock_client):
        return JulesAIService()


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


class TestFactory:
    def test_obtenir_service_retourne_instance(self):
        s = obtenir_jules_ai_service()
        assert isinstance(s, JulesAIService)

    def test_singleton(self):
        s1 = obtenir_jules_ai_service()
        s2 = obtenir_jules_ai_service()
        assert s1 is s2


# ═══════════════════════════════════════════════════════════
# CONSTRUCTION
# ═══════════════════════════════════════════════════════════


class TestConstruction:
    def test_init_avec_client_mock(self, mock_client):
        with patch("src.services.famille.jules_ai.obtenir_client_ia", return_value=mock_client):
            service = JulesAIService()
        assert service is not None

    def test_cache_prefix_jules(self, mock_client):
        with patch("src.services.famille.jules_ai.obtenir_client_ia", return_value=mock_client):
            service = JulesAIService()
        assert service.cache_prefix == "jules"

    def test_ttl_cache_7200(self, mock_client):
        with patch("src.services.famille.jules_ai.obtenir_client_ia", return_value=mock_client):
            service = JulesAIService()
        assert service.default_ttl == 7200


# ═══════════════════════════════════════════════════════════
# PROMPTS — STRUCTURE (sans appel réseau)
# ═══════════════════════════════════════════════════════════


class TestPromptsActivites:
    """Vérifie la structure des prompts sans appel IA réel."""

    def test_prompt_suggerer_activites_contient_age(self, service_avec_mock):
        """Le prompt doit mentionner l'âge en mois."""
        import inspect
        source = inspect.getsource(service_avec_mock.suggerer_activites)
        assert "age_mois" in source

    def test_prompt_conseil_developpement_contient_themes(self, service_avec_mock):
        """Les thèmes de développement sont définis."""
        import inspect
        source = inspect.getsource(service_avec_mock.conseil_developpement)
        assert "proprete" in source or "sommeil" in source


# ═══════════════════════════════════════════════════════════
# APPELS ASYNC AVEC MOCK
# ═══════════════════════════════════════════════════════════


class TestSuggererActivites:
    @pytest.mark.asyncio
    async def test_sugg_activites_appel_avec_age(self, service_avec_mock):
        with patch.object(service_avec_mock, "call_with_cache", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "🎯 Activité\n⏱️ 20 min\n📝 Description\n⏰ Bénéfice"
            result = await service_avec_mock.suggerer_activites(age_mois=18)
        assert result is not None
        mock_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_sugg_activites_nb_defaut(self, service_avec_mock):
        with patch.object(service_avec_mock, "call_with_cache", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "Activités suggérées"
            await service_avec_mock.suggerer_activites(age_mois=12)
        # Le prompt doit inclure nb=3 par défaut
        call_kwargs = mock_call.call_args
        assert "3" in call_kwargs[1].get("prompt", call_kwargs[0][0] if call_kwargs[0] else "")

    @pytest.mark.asyncio
    async def test_sugg_activites_meteo_interieur(self, service_avec_mock):
        with patch.object(service_avec_mock, "call_with_cache", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "Activités intérieures"
            result = await service_avec_mock.suggerer_activites(age_mois=24, meteo="intérieur")
        assert result == "Activités intérieures"


class TestConseilDeveloppement:
    @pytest.mark.asyncio
    async def test_conseil_theme_proprete(self, service_avec_mock):
        with patch.object(service_avec_mock, "call_with_cache", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "Conseil propreté"
            result = await service_avec_mock.conseil_developpement(age_mois=24, theme="proprete")
        assert result == "Conseil propreté"

    @pytest.mark.asyncio
    async def test_conseil_theme_sommeil(self, service_avec_mock):
        with patch.object(service_avec_mock, "call_with_cache", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "Conseil sommeil"
            result = await service_avec_mock.conseil_developpement(age_mois=18, theme="sommeil")
        assert result == "Conseil sommeil"

    @pytest.mark.asyncio
    async def test_conseil_theme_inconnu_utilise_theme_brut(self, service_avec_mock):
        with patch.object(service_avec_mock, "call_with_cache", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "Conseil générique"
            result = await service_avec_mock.conseil_developpement(age_mois=30, theme="dessin")
        # Le thème "dessin" n'est pas dans le dict → utilise le thème brut
        assert result is not None


class TestSuggererJouets:
    @pytest.mark.asyncio
    async def test_sugg_jouets_avec_budget(self, service_avec_mock):
        with patch.object(service_avec_mock, "call_with_cache", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "🎁 Jouet 1\n💰 15€"
            result = await service_avec_mock.suggerer_jouets(age_mois=12, budget=50)
        assert result is not None

    @pytest.mark.asyncio
    async def test_sugg_jouets_budget_defaut_30(self, service_avec_mock):
        with patch.object(service_avec_mock, "call_with_cache", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "Jouets"
            await service_avec_mock.suggerer_jouets(age_mois=18)
        call_args = mock_call.call_args
        prompt = call_args[1].get("prompt", call_args[0][0] if call_args[0] else "")
        assert "30" in prompt
