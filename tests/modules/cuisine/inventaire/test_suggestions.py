"""
Tests pour src/modules/cuisine/inventaire/suggestions.py

Tests complets pour render_suggestions_ia() avec mocking Streamlit.
"""

from unittest.mock import MagicMock, patch

import pytest


class SuggestionMock:
    """Mock d'une suggestion IA"""

    def __init__(
        self,
        nom: str,
        priorite: str,
        quantite: float = 1,
        unite: str = "kg",
        rayon: str = "Épicerie",
    ):
        self.nom = nom
        self.priorite = priorite
        self.quantite = quantite
        self.unite = unite
        self.rayon = rayon


class TestRenderSuggestionsIA:
    """Tests pour render_suggestions_ia()"""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit"""
        with patch("src.modules.cuisine.inventaire.suggestions.st") as mock:
            mock.session_state = {}
            mock.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
            yield mock

    @pytest.fixture
    def mock_service(self):
        """Mock inventaire service"""
        with patch("src.modules.cuisine.inventaire.suggestions.get_inventaire_service") as mock:
            mock_svc = MagicMock()
            mock.return_value = mock_svc
            yield mock_svc

    def test_affiche_erreur_si_service_none(self, mock_st):
        """Vérifie l'erreur si service indisponible"""
        with patch("src.modules.cuisine.inventaire.suggestions.get_inventaire_service") as mock:
            mock.return_value = None

            from src.modules.cuisine.inventaire.suggestions import render_suggestions_ia

            render_suggestions_ia()

            mock_st.error.assert_called_once()
            assert "indisponible" in mock_st.error.call_args[0][0]

    def test_affiche_info_ia(self, mock_st, mock_service):
        """Vérifie l'affichage du message info IA"""
        mock_st.button.return_value = False

        from src.modules.cuisine.inventaire.suggestions import render_suggestions_ia

        render_suggestions_ia()

        mock_st.info.assert_called_once()
        assert "IA" in mock_st.info.call_args[0][0]

    def test_initialise_session_state(self, mock_st, mock_service):
        """Vérifie l'initialisation du session_state"""
        mock_st.button.return_value = False

        from src.modules.cuisine.inventaire.suggestions import render_suggestions_ia

        render_suggestions_ia()

        assert "suggestions_data" in mock_st.session_state

    def test_bouton_generer_suggestions(self, mock_st, mock_service):
        """Vérifie la présence du bouton"""
        mock_st.button.return_value = False

        from src.modules.cuisine.inventaire.suggestions import render_suggestions_ia

        render_suggestions_ia()

        mock_st.button.assert_called()
        assert "Générer" in str(mock_st.button.call_args)

    def test_genere_suggestions_au_clic(self, mock_st, mock_service):
        """Vérifie la génération au clic"""
        mock_st.button.return_value = True
        mock_service.suggerer_courses_ia.return_value = [SuggestionMock("Pommes", "haute")]

        from src.modules.cuisine.inventaire.suggestions import render_suggestions_ia

        render_suggestions_ia()

        mock_service.suggerer_courses_ia.assert_called_once()
        mock_st.spinner.assert_called()

    def test_affiche_warning_si_aucune_suggestion(self, mock_st, mock_service):
        """Vérifie le warning si pas de suggestions"""
        mock_st.button.return_value = True
        mock_service.suggerer_courses_ia.return_value = []

        from src.modules.cuisine.inventaire.suggestions import render_suggestions_ia

        render_suggestions_ia()

        mock_st.warning.assert_called()

    def test_stocke_suggestions_en_session(self, mock_st, mock_service):
        """Vérifie le stockage des suggestions"""
        mock_st.button.return_value = True
        suggestions = [SuggestionMock("Lait", "moyenne")]
        mock_service.suggerer_courses_ia.return_value = suggestions

        from src.modules.cuisine.inventaire.suggestions import render_suggestions_ia

        render_suggestions_ia()

        assert mock_st.session_state["suggestions_data"] == suggestions

    def test_affiche_suggestions_existantes(self, mock_st, mock_service):
        """Vérifie l'affichage des suggestions en session"""
        mock_st.button.return_value = False
        mock_st.session_state = {
            "suggestions_data": [
                SuggestionMock("Pommes", "haute"),
                SuggestionMock("Pain", "basse"),
            ]
        }

        mock_expander = MagicMock()
        mock_expander.__enter__ = MagicMock(return_value=mock_expander)
        mock_expander.__exit__ = MagicMock(return_value=False)
        mock_st.expander.return_value = mock_expander

        from src.modules.cuisine.inventaire.suggestions import render_suggestions_ia

        render_suggestions_ia()

        mock_st.success.assert_called()
        mock_st.expander.assert_called()

    def test_groupe_par_priorite(self, mock_st, mock_service):
        """Vérifie le groupement par priorité"""
        mock_st.button.return_value = False
        mock_st.session_state = {
            "suggestions_data": [
                SuggestionMock("Pommes", "haute"),
                SuggestionMock("Carottes", "haute"),
                SuggestionMock("Pain", "basse"),
            ]
        }

        mock_expander = MagicMock()
        mock_expander.__enter__ = MagicMock(return_value=mock_expander)
        mock_expander.__exit__ = MagicMock(return_value=False)
        mock_st.expander.return_value = mock_expander

        from src.modules.cuisine.inventaire.suggestions import render_suggestions_ia

        render_suggestions_ia()

        # Vérifie qu'expander a été appelé pour haute et basse
        assert mock_st.expander.call_count >= 2

    def test_gere_exception(self, mock_st, mock_service):
        """Vérifie la gestion d'erreur"""
        mock_st.button.return_value = True
        mock_service.suggerer_courses_ia.side_effect = Exception("API Error")

        from src.modules.cuisine.inventaire.suggestions import render_suggestions_ia

        render_suggestions_ia()

        mock_st.error.assert_called()


class TestSuggestionsExports:
    """Tests des exports"""

    def test_import_render_suggestions_ia(self):
        """Vérifie l'import"""
        from src.modules.cuisine.inventaire.suggestions import render_suggestions_ia

        assert callable(render_suggestions_ia)

    def test_all_exports(self):
        """Vérifie __all__"""
        from src.modules.cuisine.inventaire.suggestions import __all__

        assert "render_suggestions_ia" in __all__
