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
    """Tests pour afficher_detail_recette."""

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_recette_basic(self, mock_st, mock_svc_factory, mock_render_img) -> None:
        """Test afficher_detail_recette sans erreur."""
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {"nb_cuissons": 5}
        mock_service.get_historique.return_value = []
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service

        recette = create_mock_recette()
        afficher_detail_recette(recette)

        mock_st.header.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_with_image(self, mock_st, mock_svc_factory, mock_render_img) -> None:
        """Test avec image."""
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service

        recette = create_mock_recette(with_image=True)
        afficher_detail_recette(recette)

        # L'image est affichée via st.markdown avec HTML <img> tag
        mock_st.markdown.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_difficulte_moyen(
        self, mock_st, mock_svc_factory, mock_render_img
    ) -> None:
        """Test difficulte moyenne."""
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service

        recette = create_mock_recette()
        recette.difficulte = "moyen"
        afficher_detail_recette(recette)

        mock_st.markdown.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_difficulte_difficile(
        self, mock_st, mock_svc_factory, mock_render_img
    ) -> None:
        """Test difficulte difficile."""
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service

        recette = create_mock_recette()
        recette.difficulte = "difficile"
        afficher_detail_recette(recette)

        mock_st.markdown.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_with_robots(self, mock_st, mock_svc_factory, mock_render_img) -> None:
        """Test avec robots menagers."""
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service

        recette = create_mock_recette(with_robots=True)
        afficher_detail_recette(recette)

        mock_st.markdown.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_no_nutrition(self, mock_st, mock_svc_factory, mock_render_img) -> None:
        """Test sans nutrition."""
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service

        recette = create_mock_recette(with_nutrition=False)
        afficher_detail_recette(recette)

        mock_st.metric.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_with_historique(
        self, mock_st, mock_svc_factory, mock_render_img
    ) -> None:
        """Test avec historique."""
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

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
        afficher_detail_recette(recette)

        mock_st.metric.assert_called()


class TestImports:
    """Tests des imports."""

    def test_import_render_detail_recette(self) -> None:
        """Test import afficher_detail_recette."""
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        assert callable(afficher_detail_recette)


@pytest.mark.unit
class TestRenderDetailRecetteExtended:
    """Tests etendus pour afficher_detail_recette."""

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_image_exception(self, mock_st, mock_svc_factory, mock_render_img):
        """Test quand l image ne peut pas etre chargee."""
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_st.image.side_effect = Exception("Image error")
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette(with_image=True)
        afficher_detail_recette(recette)
        mock_st.caption.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_no_badges(self, mock_st, mock_svc_factory, mock_render_img):
        """Test sans badges."""
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.est_bio = False
        recette.est_local = False
        recette.est_rapide = False
        recette.est_equilibre = False
        recette.congelable = False
        recette.score_bio = 0
        recette.score_local = 0
        afficher_detail_recette(recette)
        mock_st.header.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_detail_all_badges(self, mock_st, mock_svc_factory, mock_render_img):
        """Test avec tous les badges."""
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.est_bio = True
        recette.est_local = True
        recette.est_rapide = True
        recette.est_equilibre = True
        recette.congelable = True
        afficher_detail_recette(recette)
        mock_st.markdown.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_render_robots_iteration(self, mock_st, mock_svc_factory, mock_render_img):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions_recette.return_value = []
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette(with_robots=True)
        recette.robots_compatibles = ["Cookeo", "Monsieur Cuisine", "Airfryer"]
        afficher_detail_recette(recette)
        mock_st.markdown.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_cuisson_button_clicked(self, mock_st, mock_svc_factory, mock_render_img):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [True] + [False] * 10
        mock_st.form_submit_button.return_value = False
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {"nb_cuissons": 5}
        mock_service.get_historique.return_value = []
        mock_service.get_versions.return_value = []
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        afficher_detail_recette(recette)
        mock_st.form.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_cuisson_form_submit_success(self, mock_st, mock_svc_factory, mock_render_img):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [True] + [False] * 10
        mock_st.form_submit_button.return_value = True
        mock_st.number_input.return_value = 4
        mock_st.slider.return_value = 4
        mock_st.text_area.return_value = "Excellent"
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {"nb_cuissons": 5}
        mock_service.get_historique.return_value = []
        mock_service.get_versions.return_value = []
        mock_service.enregistrer_cuisson.return_value = True
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        afficher_detail_recette(recette)
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_cuisson_form_submit_failure(self, mock_st, mock_svc_factory, mock_render_img):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [True] + [False] * 10
        mock_st.form_submit_button.return_value = True
        mock_st.number_input.return_value = 4
        mock_st.slider.return_value = 0
        mock_st.text_area.return_value = ""
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {"nb_cuissons": 5}
        mock_service.get_historique.return_value = []
        mock_service.get_versions.return_value = []
        mock_service.enregistrer_cuisson.return_value = False
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        afficher_detail_recette(recette)
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_historique_avec_avis(self, mock_st, mock_svc_factory, mock_render_img):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

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
        hist_item.portions_cuisinees = 4
        hist_item.note = 5
        hist_item.avis = "Tres bonne!"
        mock_service.get_historique.return_value = [hist_item]
        mock_service.get_versions.return_value = []
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        afficher_detail_recette(recette)
        mock_st.caption.assert_called()

    @patch("src.modules.cuisine.recettes.detail.etat_vide")
    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_versions_vides(self, mock_st, mock_svc_factory, mock_render_img, mock_etat_vide):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions.return_value = []
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        afficher_detail_recette(recette)
        mock_etat_vide.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_generer_bebe_success(self, mock_st, mock_svc_factory, mock_render_img):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [False, True] + [False] * 10
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions.return_value = []
        mock_service.generer_version_bebe.return_value = MagicMock()
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        afficher_detail_recette(recette)
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_generer_bebe_failure(self, mock_st, mock_svc_factory, mock_render_img):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [False, True] + [False] * 10
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions.return_value = []
        mock_service.generer_version_bebe.return_value = None
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        afficher_detail_recette(recette)
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_generer_bebe_exception(self, mock_st, mock_svc_factory, mock_render_img):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [False, True] + [False] * 10
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions.return_value = []
        mock_service.generer_version_bebe.side_effect = Exception("Erreur IA")
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        afficher_detail_recette(recette)
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_generer_batch_success(self, mock_st, mock_svc_factory, mock_render_img):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [False, False, True] + [False] * 10
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions.return_value = []
        mock_service.generer_version_batch_cooking.return_value = MagicMock()
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        afficher_detail_recette(recette)
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_generer_batch_failure(self, mock_st, mock_svc_factory, mock_render_img):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [False, False, True] + [False] * 10
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions.return_value = []
        mock_service.generer_version_batch_cooking.return_value = None
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        afficher_detail_recette(recette)
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_generer_batch_exception(self, mock_st, mock_svc_factory, mock_render_img):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [False, False, True] + [False] * 10
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions.return_value = []
        mock_service.generer_version_batch_cooking.side_effect = Exception("Erreur")
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        afficher_detail_recette(recette)
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_action_dupliquer_success(self, mock_st, mock_svc_factory, mock_render_img):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [False, False, False, False, True] + [False] * 10
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions.return_value = []
        mock_service.create.return_value = MagicMock()
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.type_repas = "dessert"
        recette.categorie = "patisserie"
        recette.saison = "ete"
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        afficher_detail_recette(recette)
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_action_dupliquer_exception(self, mock_st, mock_svc_factory, mock_render_img):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [False, False, False, False, True] + [False] * 10
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions.return_value = []
        mock_service.create.side_effect = Exception("Erreur")
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.type_repas = "dessert"
        recette.categorie = "patisserie"
        recette.saison = "ete"
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        afficher_detail_recette(recette)
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes.detail.time")
    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_action_supprimer_success(self, mock_st, mock_svc_factory, mock_render_img, mock_time):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [False, False, False, False, False, True] + [False] * 10
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions.return_value = []
        mock_service.delete.return_value = True
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        afficher_detail_recette(recette)
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_action_supprimer_failure(self, mock_st, mock_svc_factory, mock_render_img):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [False, False, False, False, False, True] + [False] * 10
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions.return_value = []
        mock_service.delete.return_value = False
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        afficher_detail_recette(recette)
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes.detail.afficher_generer_image")
    @patch("src.modules.cuisine.recettes.detail.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.detail.st")
    def test_action_supprimer_exception(self, mock_st, mock_svc_factory, mock_render_img):
        from src.modules.cuisine.recettes.detail import afficher_detail_recette

        setup_mock_st(mock_st)
        mock_st.button.side_effect = [False, False, False, False, False, True] + [False] * 10
        mock_service = MagicMock()
        mock_service.get_stats_recette.return_value = {}
        mock_service.get_historique.return_value = []
        mock_service.get_versions.return_value = []
        mock_service.delete.side_effect = Exception("Erreur")
        mock_svc_factory.return_value = mock_service
        recette = create_mock_recette()
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False
        recette.compatible_multicooker = False
        afficher_detail_recette(recette)
        mock_st.error.assert_called()
