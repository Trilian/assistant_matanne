"""
Tests pour JeuxAIService - Analyse IA des opportunitÃ©s.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.jeux import (
    SEUIL_VALUE_ALERTE,
    SEUIL_VALUE_HAUTE,
    AnalyseIA,
    JeuxAIService,
    OpportuniteAnalysee,
    obtenir_jeux_ai_service,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture
def service():
    """Instance du service IA."""
    return JeuxAIService()


@pytest.fixture
def mock_client_ia():
    """Mock du ClientIA et BaseAIService.call_with_cache."""
    with (
        patch("src.services.jeux._internal.ai_service.obtenir_client_ia") as mock_obtenir,
        patch.object(JeuxAIService, "call_with_cache", new_callable=AsyncMock) as mock_call,
    ):
        client_instance = MagicMock()
        mock_obtenir.return_value = client_instance
        yield mock_call


@pytest.fixture
def opportunites_paris():
    """DonnÃ©es d'opportunitÃ©s Paris sportifs."""
    return [
        {"marche": "More_2_5", "value": 2.8, "serie": 14, "frequence": 0.20},
        {"marche": "BTTS_Yes", "value": 2.3, "serie": 11, "frequence": 0.21},
        {"marche": "1X", "value": 1.9, "serie": 8, "frequence": 0.24},
    ]


@pytest.fixture
def numeros_loto():
    """DonnÃ©es de numÃ©ros Loto en retard."""
    return [
        {"numero": 7, "value": 3.1, "serie": 30, "frequence": 0.103},
        {"numero": 23, "value": 2.5, "serie": 24, "frequence": 0.104},
        {"numero": 42, "value": 2.1, "serie": 20, "frequence": 0.105},
    ]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CLIENT IA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestJeuxAIServiceInit:
    """Tests d'initialisation du service."""

    def test_init(self, service):
        """Le service s'initialise correctement."""
        assert service._client_ia is None
        assert service.service_name == "jeux"
        assert service.cache_prefix == "jeux"
        assert service.default_temperature == 0.3

    def test_lazy_client(self, service, mock_client_ia):
        """Le client est chargÃ© en lazy loading."""
        _ = service.client
        assert service._client_ia is not None

    def test_inherits_base_ai(self, service):
        """Le service hÃ©rite bien de BaseAIService."""
        from src.services.core.base.ai_service import BaseAIService

        assert isinstance(service, BaseAIService)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ANALYSE PARIS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAnalyserParis:
    """Tests de l'analyse Paris sportifs."""

    def test_analyse_vide(self, service):
        """Analyse avec liste vide retourne rÃ©sultat par dÃ©faut."""
        result = service.analyser_paris([])

        assert isinstance(result, AnalyseIA)
        assert result.type_analyse == "paris"
        assert "Aucune opportunité" in result.resume
        assert result.confiance == 0.0

    @pytest.mark.asyncio
    async def test_analyse_avec_donnees(self, service, opportunites_paris, mock_client_ia):
        """Analyse avec donnÃ©es appelle l'IA."""
        mock_client_ia.return_value = """
            RÃ©sumÃ© de l'analyse Paris sportifs.

            Points clÃ©s:
            - 3 opportunitÃ©s dÃ©tectÃ©es
            - More_2_5 trÃ¨s en retard

            Recommandations:
            - Surveiller le marchÃ© More_2_5
            """

        result = await service.analyser_paris_async(opportunites_paris)

        assert isinstance(result, AnalyseIA)
        assert result.type_analyse == "paris"
        mock_client_ia.assert_called_once()

    def test_construire_prompt_paris(self, service, opportunites_paris):
        """Le prompt Paris est correctement construit."""
        prompt = service._construire_prompt_paris(opportunites_paris, "Ligue 1")

        assert "Ligue 1" in prompt
        assert "More_2_5" in prompt
        assert "Value=" in prompt
        assert "Série=" in prompt

    def test_fallback_sans_ia(self, service, opportunites_paris):
        """Fallback gÃ©nÃ¨re une analyse basique sans IA."""
        result = service._analyse_fallback("paris", opportunites_paris)

        assert result.type_analyse == "paris"
        assert "3" in result.resume  # 3 opportunitÃ©s
        assert result.confiance == 0.3


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ANALYSE LOTO
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAnalyserLoto:
    """Tests de l'analyse Loto."""

    def test_analyse_vide(self, service):
        """Analyse avec liste vide retourne rÃ©sultat par dÃ©faut."""
        result = service.analyser_loto([])

        assert isinstance(result, AnalyseIA)
        assert result.type_analyse == "loto"
        assert "Aucun numéro" in result.resume

    @pytest.mark.asyncio
    async def test_analyse_avec_donnees(self, service, numeros_loto, mock_client_ia):
        """Analyse avec donnÃ©es appelle l'IA."""
        mock_client_ia.return_value = """
            Analyse des numÃ©ros en retard.

            Points clÃ©s:
            - Le numÃ©ro 7 n'est pas sorti depuis 30 tirages

            Recommandations:
            - Rappel: chaque tirage est indÃ©pendant
            """

        result = await service.analyser_loto_async(numeros_loto)

        assert isinstance(result, AnalyseIA)
        assert result.type_analyse == "loto"

    def test_construire_prompt_loto(self, service, numeros_loto):
        """Le prompt Loto est correctement construit."""
        prompt = service._construire_prompt_loto(numeros_loto, "principal")

        assert "Numéro 7" in prompt
        assert "30 tirages" in prompt
        assert "INDÉPENDANT" in prompt


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SYNTHÃˆSE GLOBALE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGenererSynthese:
    """Tests de la gÃ©nÃ©ration de synthÃ¨se."""

    @pytest.mark.asyncio
    async def test_synthese(self, service, mock_client_ia):
        """SynthÃ¨se gÃ©nÃ¨re un rÃ©sumÃ© global."""
        mock_client_ia.return_value = "SynthÃ¨se globale des opportunitÃ©s."

        result = await service.generer_synthese_async(
            alertes_actives=5,
            opportunites_paris=10,
            opportunites_loto=8,
        )

        assert isinstance(result, AnalyseIA)
        assert result.type_analyse == "global"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PARSING RÃ‰PONSE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestParserReponse:
    """Tests du parsing des rÃ©ponses IA."""

    def test_parser_reponse_complete(self, service):
        """Parse une rÃ©ponse IA complÃ¨te."""
        reponse = """
        Ceci est le rÃ©sumÃ© de l'analyse.

        Points clÃ©s:
        - Premier point
        - DeuxiÃ¨me point

        recommandations:
        - PremiÃ¨re recommandation
        - DeuxiÃ¨me recommandation
        """

        result = service._parser_reponse_analyse(reponse, "paris")

        assert "résumé" in result.resume.lower()
        assert len(result.points_cles) >= 1  # Parser best-effort
        assert len(result.recommandations) >= 1  # Parser best-effort

    def test_parser_reponse_simple(self, service):
        """Parse une rÃ©ponse simple sans sections."""
        reponse = "Analyse simple sans structure."

        result = service._parser_reponse_analyse(reponse, "loto")

        assert result.resume == "Analyse simple sans structure."
        assert len(result.points_cles) >= 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FACTORY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFactory:
    """Tests de la factory."""

    def test_get_jeux_ai_service(self):
        """Factory retourne une instance singleton."""
        service1 = obtenir_jeux_ai_service()
        service2 = obtenir_jeux_ai_service()

        assert service1 is service2
        assert isinstance(service1, JeuxAIService)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS AVERTISSEMENTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAvertissements:
    """Tests des avertissements sur le hasard."""

    def test_avertissement_standard(self, service):
        """L'avertissement standard est prÃ©sent."""
        assert "hasard" in service.AVERTISSEMENT_STANDARD.lower()
        assert "garantit" in service.AVERTISSEMENT_STANDARD.lower()

    def test_system_prompt_rappel_hasard(self, service):
        """Le prompt systÃ¨me rappelle le hasard."""
        assert "INDÉPENDANT" in service.SYSTEM_PROMPT
        assert "IMPRÃ‰VISIBLES" in service.SYSTEM_PROMPT

    def test_analyse_contient_avertissement(self, service, opportunites_paris):
        """Toute analyse contient un avertissement."""
        result = service._analyse_fallback("paris", opportunites_paris)

        assert result.avertissement == service.AVERTISSEMENT_STANDARD

