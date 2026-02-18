"""
Tests pour JeuxAIService - Analyse IA des opportunités.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.jeux.ai_service import (
    AnalyseIA,
    JeuxAIService,
    OpportuniteAnalysee,
    get_jeux_ai_service,
)
from src.services.jeux.series_service import SEUIL_VALUE_ALERTE, SEUIL_VALUE_HAUTE

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def service():
    """Instance du service IA."""
    return JeuxAIService()


@pytest.fixture
def mock_client_ia():
    """Mock du ClientIA."""
    with patch("src.services.jeux._internal.ai_service.ClientIA") as mock:
        client_instance = MagicMock()
        mock.return_value = client_instance
        yield client_instance


@pytest.fixture
def opportunites_paris():
    """Données d'opportunités Paris sportifs."""
    return [
        {"marche": "More_2_5", "value": 2.8, "serie": 14, "frequence": 0.20},
        {"marche": "BTTS_Yes", "value": 2.3, "serie": 11, "frequence": 0.21},
        {"marche": "1X", "value": 1.9, "serie": 8, "frequence": 0.24},
    ]


@pytest.fixture
def numeros_loto():
    """Données de numéros Loto en retard."""
    return [
        {"numero": 7, "value": 3.1, "serie": 30, "frequence": 0.103},
        {"numero": 23, "value": 2.5, "serie": 24, "frequence": 0.104},
        {"numero": 42, "value": 2.1, "serie": 20, "frequence": 0.105},
    ]


# ═══════════════════════════════════════════════════════════
# TESTS CLIENT IA
# ═══════════════════════════════════════════════════════════


class TestJeuxAIServiceInit:
    """Tests d'initialisation du service."""

    def test_init(self, service):
        """Le service s'initialise correctement."""
        assert service._client is None

    def test_lazy_client(self, service, mock_client_ia):
        """Le client est chargé en lazy loading."""
        _ = service.client
        assert service._client is not None


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSE PARIS
# ═══════════════════════════════════════════════════════════


class TestAnalyserParis:
    """Tests de l'analyse Paris sportifs."""

    def test_analyse_vide(self, service):
        """Analyse avec liste vide retourne résultat par défaut."""
        result = service.analyser_paris([])

        assert isinstance(result, AnalyseIA)
        assert result.type_analyse == "paris"
        assert "Aucune opportunité" in result.resume
        assert result.confiance == 0.0

    @pytest.mark.asyncio
    async def test_analyse_avec_donnees(self, service, opportunites_paris, mock_client_ia):
        """Analyse avec données appelle l'IA."""
        mock_client_ia.appeler = AsyncMock(
            return_value="""
            Résumé de l'analyse Paris sportifs.

            Points clés:
            - 3 opportunités détectées
            - More_2_5 très en retard

            Recommandations:
            - Surveiller le marché More_2_5
            """
        )

        result = await service.analyser_paris_async(opportunites_paris)

        assert isinstance(result, AnalyseIA)
        assert result.type_analyse == "paris"
        mock_client_ia.appeler.assert_called_once()

    def test_construire_prompt_paris(self, service, opportunites_paris):
        """Le prompt Paris est correctement construit."""
        prompt = service._construire_prompt_paris(opportunites_paris, "Ligue 1")

        assert "Ligue 1" in prompt
        assert "More_2_5" in prompt
        assert "Value=" in prompt
        assert "Série=" in prompt

    def test_fallback_sans_ia(self, service, opportunites_paris):
        """Fallback génère une analyse basique sans IA."""
        result = service._analyse_fallback("paris", opportunites_paris)

        assert result.type_analyse == "paris"
        assert "3" in result.resume  # 3 opportunités
        assert result.confiance == 0.3


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSE LOTO
# ═══════════════════════════════════════════════════════════


class TestAnalyserLoto:
    """Tests de l'analyse Loto."""

    def test_analyse_vide(self, service):
        """Analyse avec liste vide retourne résultat par défaut."""
        result = service.analyser_loto([])

        assert isinstance(result, AnalyseIA)
        assert result.type_analyse == "loto"
        assert "Aucun numéro" in result.resume

    @pytest.mark.asyncio
    async def test_analyse_avec_donnees(self, service, numeros_loto, mock_client_ia):
        """Analyse avec données appelle l'IA."""
        mock_client_ia.appeler = AsyncMock(
            return_value="""
            Analyse des numéros en retard.

            Points clés:
            - Le numéro 7 n'est pas sorti depuis 30 tirages

            Recommandations:
            - Rappel: chaque tirage est indépendant
            """
        )

        result = await service.analyser_loto_async(numeros_loto)

        assert isinstance(result, AnalyseIA)
        assert result.type_analyse == "loto"

    def test_construire_prompt_loto(self, service, numeros_loto):
        """Le prompt Loto est correctement construit."""
        prompt = service._construire_prompt_loto(numeros_loto, "principal")

        assert "Numéro 7" in prompt
        assert "30 tirages" in prompt
        assert "INDÉPENDANT" in prompt


# ═══════════════════════════════════════════════════════════
# TESTS SYNTHÈSE GLOBALE
# ═══════════════════════════════════════════════════════════


class TestGenererSynthese:
    """Tests de la génération de synthèse."""

    @pytest.mark.asyncio
    async def test_synthese(self, service, mock_client_ia):
        """Synthèse génère un résumé global."""
        mock_client_ia.appeler = AsyncMock(return_value="Synthèse globale des opportunités.")

        result = await service.generer_synthese_async(
            alertes_actives=5,
            opportunites_paris=10,
            opportunites_loto=8,
        )

        assert isinstance(result, AnalyseIA)
        assert result.type_analyse == "global"


# ═══════════════════════════════════════════════════════════
# TESTS PARSING RÉPONSE
# ═══════════════════════════════════════════════════════════


class TestParserReponse:
    """Tests du parsing des réponses IA."""

    def test_parser_reponse_complete(self, service):
        """Parse une réponse IA complète."""
        reponse = """
        Ceci est le résumé de l'analyse.

        Points clés:
        - Premier point
        - Deuxième point

        recommandations:
        - Première recommandation
        - Deuxième recommandation
        """

        result = service._parser_reponse_analyse(reponse, "paris")

        assert "résumé" in result.resume.lower()
        assert len(result.points_cles) >= 1  # Parser best-effort
        assert len(result.recommandations) >= 1  # Parser best-effort

    def test_parser_reponse_simple(self, service):
        """Parse une réponse simple sans sections."""
        reponse = "Analyse simple sans structure."

        result = service._parser_reponse_analyse(reponse, "loto")

        assert result.resume == "Analyse simple sans structure."
        assert len(result.points_cles) >= 1


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY
# ═══════════════════════════════════════════════════════════


class TestFactory:
    """Tests de la factory."""

    def test_get_jeux_ai_service(self):
        """Factory retourne une instance singleton."""
        service1 = get_jeux_ai_service()
        service2 = get_jeux_ai_service()

        assert service1 is service2
        assert isinstance(service1, JeuxAIService)


# ═══════════════════════════════════════════════════════════
# TESTS AVERTISSEMENTS
# ═══════════════════════════════════════════════════════════


class TestAvertissements:
    """Tests des avertissements sur le hasard."""

    def test_avertissement_standard(self, service):
        """L'avertissement standard est présent."""
        assert "hasard" in service.AVERTISSEMENT_STANDARD.lower()
        assert "garantit" in service.AVERTISSEMENT_STANDARD.lower()

    def test_system_prompt_rappel_hasard(self, service):
        """Le prompt système rappelle le hasard."""
        assert "INDÉPENDANT" in service.SYSTEM_PROMPT
        assert "IMPRÉVISIBLES" in service.SYSTEM_PROMPT

    def test_analyse_contient_avertissement(self, service, opportunites_paris):
        """Toute analyse contient un avertissement."""
        result = service._analyse_fallback("paris", opportunites_paris)

        assert result.avertissement == service.AVERTISSEMENT_STANDARD
