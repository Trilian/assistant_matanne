"""
Tests pour src/modules/cuisine/planificateur_repas/generation.py

Tests complets pour generer_semaine_ia().
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest


class TestGenererSemaineIA:
    """Tests pour generer_semaine_ia()"""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit"""
        with patch("src.modules.cuisine.planificateur_repas.generation.st") as mock:
            yield mock

    @pytest.fixture
    def mock_logger(self):
        """Mock logger"""
        with patch("src.modules.cuisine.planificateur_repas.generation.logger") as mock:
            yield mock

    @pytest.fixture
    def mock_preferences(self):
        """Mock charger_preferences"""
        with patch(
            "src.modules.cuisine.planificateur_repas.generation.charger_preferences"
        ) as mock:
            mock.return_value = {"regime": "equilibre", "budget": "moyen"}
            yield mock

    @pytest.fixture
    def mock_feedbacks(self):
        """Mock charger_feedbacks"""
        with patch("src.modules.cuisine.planificateur_repas.generation.charger_feedbacks") as mock:
            mock.return_value = []
            yield mock

    @pytest.fixture
    def mock_prompt(self):
        """Mock generer_prompt_semaine"""
        with patch(
            "src.modules.cuisine.planificateur_repas.generation.generer_prompt_semaine"
        ) as mock:
            mock.return_value = "Génère un planning de repas pour la semaine"
            yield mock

    @pytest.fixture
    def mock_client_ia(self):
        """Mock obtenir_client_ia"""
        with patch("src.modules.cuisine.planificateur_repas.generation.obtenir_client_ia") as mock:
            yield mock

    def test_retourne_dict_vide_si_client_ia_none(
        self, mock_st, mock_preferences, mock_feedbacks, mock_prompt, mock_client_ia
    ):
        """Teste le comportement sans client IA"""
        mock_client_ia.return_value = None

        from src.modules.cuisine.planificateur_repas.generation import generer_semaine_ia

        result = generer_semaine_ia(date(2025, 1, 6))

        assert result == {}
        mock_st.error.assert_called()

    def test_retourne_response_dict_directement(
        self,
        mock_st,
        mock_preferences,
        mock_feedbacks,
        mock_prompt,
        mock_client_ia,
    ):
        """Teste le retour direct d'un dict"""
        mock_client = MagicMock()
        mock_client.generer_json.return_value = {"lundi": {"midi": "Poulet", "soir": "Pâtes"}}
        mock_client_ia.return_value = mock_client

        from src.modules.cuisine.planificateur_repas.generation import generer_semaine_ia

        result = generer_semaine_ia(date(2025, 1, 6))

        assert result == {"lundi": {"midi": "Poulet", "soir": "Pâtes"}}

    def test_parse_json_string_response(
        self,
        mock_st,
        mock_preferences,
        mock_feedbacks,
        mock_prompt,
        mock_client_ia,
    ):
        """Teste le parsing d'une réponse string JSON"""
        mock_client = MagicMock()
        mock_client.generer_json.return_value = '{"lundi": {"midi": "Poulet"}}'
        mock_client_ia.return_value = mock_client

        from src.modules.cuisine.planificateur_repas.generation import generer_semaine_ia

        result = generer_semaine_ia(date(2025, 1, 6))

        assert result == {"lundi": {"midi": "Poulet"}}

    def test_retourne_dict_vide_sur_erreur_ia(
        self,
        mock_st,
        mock_logger,
        mock_preferences,
        mock_feedbacks,
        mock_prompt,
        mock_client_ia,
    ):
        """Teste la gestion d'erreur IA"""
        mock_client = MagicMock()
        mock_client.generer_json.side_effect = Exception("API Error")
        mock_client_ia.return_value = mock_client

        from src.modules.cuisine.planificateur_repas.generation import generer_semaine_ia

        result = generer_semaine_ia(date(2025, 1, 6))

        assert result == {}
        mock_logger.error.assert_called()
        mock_st.error.assert_called()

    def test_charge_preferences_et_feedbacks(
        self,
        mock_st,
        mock_preferences,
        mock_feedbacks,
        mock_prompt,
        mock_client_ia,
    ):
        """Vérifie le chargement des préférences et feedbacks"""
        mock_client_ia.return_value = None

        from src.modules.cuisine.planificateur_repas.generation import generer_semaine_ia

        generer_semaine_ia(date(2025, 1, 6))

        mock_preferences.assert_called_once()
        mock_feedbacks.assert_called_once()

    def test_genere_prompt_avec_parametres(
        self,
        mock_st,
        mock_preferences,
        mock_feedbacks,
        mock_prompt,
        mock_client_ia,
    ):
        """Vérifie la génération du prompt"""
        mock_client_ia.return_value = None
        mock_preferences.return_value = {"regime": "vegan"}
        mock_feedbacks.return_value = [{"note": 5}]

        from src.modules.cuisine.planificateur_repas.generation import generer_semaine_ia

        generer_semaine_ia(date(2025, 1, 6))

        mock_prompt.assert_called_once_with({"regime": "vegan"}, [{"note": 5}], date(2025, 1, 6))

    def test_appelle_client_avec_bon_prompt(
        self,
        mock_st,
        mock_preferences,
        mock_feedbacks,
        mock_prompt,
        mock_client_ia,
    ):
        """Vérifie l'appel au client IA"""
        mock_client = MagicMock()
        mock_client.generer_json.return_value = {}
        mock_client_ia.return_value = mock_client
        mock_prompt.return_value = "Prompt de test"

        from src.modules.cuisine.planificateur_repas.generation import generer_semaine_ia

        generer_semaine_ia(date(2025, 1, 6))

        mock_client.generer_json.assert_called_once()
        call_kwargs = mock_client.generer_json.call_args[1]
        assert call_kwargs["prompt"] == "Prompt de test"
        assert "JSON" in call_kwargs["system_prompt"]

    def test_retourne_dict_vide_si_response_none(
        self,
        mock_st,
        mock_preferences,
        mock_feedbacks,
        mock_prompt,
        mock_client_ia,
    ):
        """Teste le cas où la réponse est None"""
        mock_client = MagicMock()
        mock_client.generer_json.return_value = None
        mock_client_ia.return_value = mock_client

        from src.modules.cuisine.planificateur_repas.generation import generer_semaine_ia

        result = generer_semaine_ia(date(2025, 1, 6))

        assert result == {}


class TestGenerationIntegration:
    """Tests d'intégration pour le module generation"""

    def test_import_generer_semaine_ia(self):
        """Vérifie que generer_semaine_ia est importable"""
        from src.modules.cuisine.planificateur_repas.generation import generer_semaine_ia

        assert callable(generer_semaine_ia)

    def test_signature_fonction(self):
        """Vérifie la signature de la fonction"""
        import inspect

        from src.modules.cuisine.planificateur_repas.generation import generer_semaine_ia

        sig = inspect.signature(generer_semaine_ia)
        params = list(sig.parameters.keys())
        assert "date_debut" in params
