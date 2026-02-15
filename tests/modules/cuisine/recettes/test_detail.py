"""
Tests pour src/modules/cuisine/recettes/detail.py
"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest


class SessionStateMock(dict):
    """Mock de st.session_state."""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


def setup_mock_st(mock_st: MagicMock, session_data: dict | None = None) -> None:
    """Configure le mock Streamlit."""
    mock_st.columns.side_effect = lambda n: [
        MagicMock() for _ in range(n if isinstance(n, int) else len(n))
    ]
    mock_st.tabs.return_value = [MagicMock() for _ in range(4)]
    mock_st.session_state = SessionStateMock(session_data or {})
    mock_st.button.return_value = False
    mock_st.form_submit_button.return_value = False
    mock_st.expander.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.form.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.form.return_value.__exit__ = MagicMock(return_value=False)


def create_mock_recette(with_image=False, with_nutrition=True, with_robots=False):
    """Cree un mock de recette."""
    recette = MagicMock()
    recette.id = 1
    recette.nom = "Tarte aux pommes"
    recette.difficulte = "facile"
    recette.url_image = "http://example.com/image.jpg" if with_image else None
    recette.est_bio = True
    recette.est_local = False
    recette.est_rapide = True
    recette.est_equilibre = True
    recette.congelable = False
    recette.score_bio = 80
    recette.score_local = 50
    recette.temps_preparation = 30
    recette.temps_cuisson = 45
    recette.portions = 6
    recette.calories = 350 if with_nutrition else None
    recette.proteines = 5 if with_nutrition else None
    recette.lipides = 15 if with_nutrition else None
    recette.glucides = 45 if with_nutrition else None
    recette.description = "Delicieuse tarte maison"
    recette.robots_compatibles = ["Cookeo", "Airfryer"] if with_robots else []

    # Ingredients
    ing = MagicMock()
    ing.ingredient = MagicMock()
    ing.ingredient.nom = "Pommes"
    ing.quantite = 500
    ing.unite = "g"
    recette.ingredients = [ing]

    # Etapes
    etape = MagicMock()
    etape.ordre = 1
    etape.description = "Preparer les pommes"
    recette.etapes = [etape]

    return recette


@pytest.mark.unit
class TestRenderDetailRecette:
    """Tests pour render_detail_recette."""

    @patch("src.modules.cuisine.recettes.detail.render_generer_image")
    @patch("src.modules.cuisine.recettes.detail.get_recette_service")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_recette_basic(self, mock_st, mock_svc_factory, mock_render_img) -> None:
        """Test render_detail_recette sans erreur."""
        from src.modules.cuisine.recettes.detail import render_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {"nb_cuissons": 5}
        mock_service.get_historique.return_value = []
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service

        recette = create_mock_recette()
        render_detail_recette(recette)

        mock_st.header.assert_called()

    @patch("src.modules.cuisine.recettes.detail.render_generer_image")
    @patch("src.modules.cuisine.recettes.detail.get_recette_service")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_with_image(self, mock_st, mock_svc_factory, mock_render_img) -> None:
        """Test avec image."""
        from src.modules.cuisine.recettes.detail import render_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service

        recette = create_mock_recette(with_image=True)
        render_detail_recette(recette)

        mock_st.image.assert_called()

    @patch("src.modules.cuisine.recettes.detail.render_generer_image")
    @patch("src.modules.cuisine.recettes.detail.get_recette_service")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_difficulte_moyen(
        self, mock_st, mock_svc_factory, mock_render_img
    ) -> None:
        """Test difficulte moyenne."""
        from src.modules.cuisine.recettes.detail import render_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service

        recette = create_mock_recette()
        recette.difficulte = "moyen"
        render_detail_recette(recette)

        mock_st.markdown.assert_called()

    @patch("src.modules.cuisine.recettes.detail.render_generer_image")
    @patch("src.modules.cuisine.recettes.detail.get_recette_service")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_difficulte_difficile(
        self, mock_st, mock_svc_factory, mock_render_img
    ) -> None:
        """Test difficulte difficile."""
        from src.modules.cuisine.recettes.detail import render_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service

        recette = create_mock_recette()
        recette.difficulte = "difficile"
        render_detail_recette(recette)

        mock_st.markdown.assert_called()

    @patch("src.modules.cuisine.recettes.detail.render_generer_image")
    @patch("src.modules.cuisine.recettes.detail.get_recette_service")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_with_robots(self, mock_st, mock_svc_factory, mock_render_img) -> None:
        """Test avec robots menagers."""
        from src.modules.cuisine.recettes.detail import render_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service

        recette = create_mock_recette(with_robots=True)
        render_detail_recette(recette)

        mock_st.markdown.assert_called()

    @patch("src.modules.cuisine.recettes.detail.render_generer_image")
    @patch("src.modules.cuisine.recettes.detail.get_recette_service")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_no_nutrition(self, mock_st, mock_svc_factory, mock_render_img) -> None:
        """Test sans nutrition."""
        from src.modules.cuisine.recettes.detail import render_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service

        recette = create_mock_recette(with_nutrition=False)
        render_detail_recette(recette)

        mock_st.metric.assert_called()

    @patch("src.modules.cuisine.recettes.detail.render_generer_image")
    @patch("src.modules.cuisine.recettes.detail.get_recette_service")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_with_historique(
        self, mock_st, mock_svc_factory, mock_render_img
    ) -> None:
        """Test avec historique."""
        from src.modules.cuisine.recettes.detail import render_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {
            "nb_cuissons": 10,
            "derniere_cuisson": "2024-01-01",
            "jours_depuis_derniere": 5,
            "note_moyenne": 4.5,
            "total_portions": 50,
        }
        hist_item = MagicMock()
        hist_item.date_cuisson.strftime.return_value = "01/01/2024"
        hist_item.portions = 4
        hist_item.note = 5
        mock_service.get_historique.return_value = [hist_item]
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service

        recette = create_mock_recette()
        render_detail_recette(recette)

        mock_st.metric.assert_called()


class TestImports:
    """Tests des imports."""

    def test_import_render_detail_recette(self) -> None:
        """Test import render_detail_recette."""
        from src.modules.cuisine.recettes.detail import render_detail_recette

        assert callable(render_detail_recette)
