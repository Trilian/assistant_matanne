"""Tests pour src/modules/cuisine/recettes/liste.py - Coverage 80%+"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest


class SessionStateMock(dict):
    """Mock de session_state Streamlit avec support attribut."""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value

    def __delattr__(self, name: str) -> None:
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)


def create_mock_recette(
    id: int = 1,
    nom: str = "Tarte aux pommes",
    difficulte: str = "facile",
    url_image: str | None = None,
    temps_preparation: int = 30,
    temps_cuisson: int = 45,
    portions: int = 6,
    score_bio: int | None = 50,
    score_local: int | None = 30,
    description: str | None = "Une delicieuse tarte",
    calories: int | None = 250,
    est_bio: bool = False,
    est_local: bool = False,
    est_rapide: bool = False,
    est_equilibre: bool = False,
    congelable: bool = False,
    compatible_cookeo: bool = False,
    compatible_monsieur_cuisine: bool = False,
    compatible_airfryer: bool = False,
    compatible_multicooker: bool = False,
    robots_compatibles: list | None = None,
) -> MagicMock:
    """Cree une recette mock configurable."""
    recette = MagicMock()
    recette.id = id
    recette.nom = nom
    recette.difficulte = difficulte
    recette.url_image = url_image
    recette.temps_preparation = temps_preparation
    recette.temps_cuisson = temps_cuisson
    recette.portions = portions
    recette.score_bio = score_bio
    recette.score_local = score_local
    recette.description = description
    recette.calories = calories
    recette.est_bio = est_bio
    recette.est_local = est_local
    recette.est_rapide = est_rapide
    recette.est_equilibre = est_equilibre
    recette.congelable = congelable
    recette.compatible_cookeo = compatible_cookeo
    recette.compatible_monsieur_cuisine = compatible_monsieur_cuisine
    recette.compatible_airfryer = compatible_airfryer
    recette.compatible_multicooker = compatible_multicooker
    recette.robots_compatibles = robots_compatibles or []
    return recette


def setup_mock_st(
    mock_st: MagicMock,
    session_data: dict | None = None,
    nom_filter: str = "",
    type_repas: str = "Tous",
    difficulte: str = "Tous",
    temps_max: int = 60,
    page_size: int = 9,
    min_score_bio: int = 0,
    min_score_local: int = 0,
    checkbox_values: dict | None = None,
    button_clicked: str | None = None,
) -> MagicMock:
    """Configure un mock complet de Streamlit."""
    default_data = {"recettes_page": 0, "recettes_page_size": page_size}
    if session_data:
        default_data.update(session_data)
    mock_st.session_state = SessionStateMock(default_data)

    def mock_columns(n, **kwargs):
        count = n if isinstance(n, int) else len(n)
        cols = []
        for _ in range(count):
            col = MagicMock()
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock(return_value=False)
            cols.append(col)
        return cols

    mock_st.columns.side_effect = mock_columns

    container_mock = MagicMock()
    container_mock.__enter__ = MagicMock(return_value=container_mock)
    container_mock.__exit__ = MagicMock(return_value=False)
    mock_st.container.return_value = container_mock

    expander_mock = MagicMock()
    expander_mock.__enter__ = MagicMock(return_value=expander_mock)
    expander_mock.__exit__ = MagicMock(return_value=False)
    mock_st.expander.return_value = expander_mock

    popover_mock = MagicMock()
    popover_mock.__enter__ = MagicMock(return_value=popover_mock)
    popover_mock.__exit__ = MagicMock(return_value=False)
    mock_st.popover.return_value = popover_mock

    spinner_mock = MagicMock()
    spinner_mock.__enter__ = MagicMock(return_value=spinner_mock)
    spinner_mock.__exit__ = MagicMock(return_value=False)
    mock_st.spinner.return_value = spinner_mock

    def selectbox_side_effect(*args, **kwargs):
        key = kwargs.get("key", "")
        if key == "select_page_size":
            return page_size
        if key == "filter_type_repas":
            return type_repas
        if key == "filter_difficulte":
            return difficulte
        return "Tous"

    mock_st.selectbox.side_effect = selectbox_side_effect
    mock_st.text_input.return_value = nom_filter
    mock_st.number_input.return_value = temps_max

    def slider_side_effect(*args, **kwargs):
        key = kwargs.get("key", "")
        if key == "filter_score_bio":
            return min_score_bio
        if key == "filter_score_local":
            return min_score_local
        return 0

    mock_st.slider.side_effect = slider_side_effect

    checkbox_data = checkbox_values or {}

    def checkbox_side_effect(*args, **kwargs):
        key = kwargs.get("key", "")
        return checkbox_data.get(key, False)

    mock_st.checkbox.side_effect = checkbox_side_effect

    def button_side_effect(*args, **kwargs):
        key = kwargs.get("key", "")
        if button_clicked and key == button_clicked:
            return True
        if args and button_clicked == args[0]:
            return True
        return False

    mock_st.button.side_effect = button_side_effect

    return mock_st


class TestImports:
    """Tests d'import."""

    def test_import_render_liste(self) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        assert callable(afficher_liste)


@pytest.mark.unit
class TestRenderListeBase:
    """Tests de base pour afficher_liste."""

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_render_liste_basic(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.search_advanced.return_value = []
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_st.columns.assert_called()

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_render_liste_no_service(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st)
        mock_svc_factory.return_value = None
        afficher_liste()
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_render_liste_with_recettes(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        recettes = [create_mock_recette(i, nom=f"Recette {i}") for i in range(5)]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_st.success.assert_called()


@pytest.mark.unit
class TestRenderListeFilters:
    """Tests pour les filtres de la liste."""

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_filter_by_nom(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, nom_filter="tarte")
        mock_service = MagicMock()
        recettes = [
            create_mock_recette(1, nom="Tarte aux pommes"),
            create_mock_recette(2, nom="Gateau chocolat"),
            create_mock_recette(3, nom="Tartelette citron"),
        ]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_filter_by_type_repas(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, type_repas="dejeuner")
        mock_service = MagicMock()
        mock_service.search_advanced.return_value = [create_mock_recette()]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        call_kwargs = mock_service.search_advanced.call_args[1]
        assert call_kwargs["type_repas"] == "dejeuner"

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_filter_by_difficulte(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, difficulte="difficile")
        mock_service = MagicMock()
        mock_service.search_advanced.return_value = [create_mock_recette()]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        call_kwargs = mock_service.search_advanced.call_args[1]
        assert call_kwargs["difficulte"] == "difficile"

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_filter_score_bio_min(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, min_score_bio=50)
        mock_service = MagicMock()
        recettes = [
            create_mock_recette(1, score_bio=60),
            create_mock_recette(2, score_bio=30),
            create_mock_recette(3, score_bio=80),
        ]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_filter_score_local_min(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, min_score_local=40)
        mock_service = MagicMock()
        recettes = [
            create_mock_recette(1, score_local=50),
            create_mock_recette(2, score_local=20),
        ]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_st.success.assert_called()


@pytest.mark.unit
class TestRenderListeRobotFilters:
    """Tests pour les filtres robots."""

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_filter_cookeo(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, checkbox_values={"robot_cookeo": True})
        mock_service = MagicMock()
        recettes = [
            create_mock_recette(1, compatible_cookeo=True),
            create_mock_recette(2, compatible_cookeo=False),
        ]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_filter_monsieur_cuisine(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, checkbox_values={"robot_mc": True})
        mock_service = MagicMock()
        recettes = [
            create_mock_recette(1, compatible_monsieur_cuisine=True),
            create_mock_recette(2, compatible_monsieur_cuisine=False),
        ]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_filter_airfryer(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, checkbox_values={"robot_airfryer": True})
        mock_service = MagicMock()
        recettes = [
            create_mock_recette(1, compatible_airfryer=True),
            create_mock_recette(2, compatible_airfryer=False),
        ]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_filter_multicooker(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, checkbox_values={"robot_multicooker": True})
        mock_service = MagicMock()
        recettes = [
            create_mock_recette(1, compatible_multicooker=True),
            create_mock_recette(2, compatible_multicooker=False),
        ]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_st.success.assert_called()


@pytest.mark.unit
class TestRenderListeTagFilters:
    """Tests pour les filtres tags."""

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_filter_rapide(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, checkbox_values={"tag_rapide": True})
        mock_service = MagicMock()
        recettes = [
            create_mock_recette(1, est_rapide=True),
            create_mock_recette(2, est_rapide=False),
        ]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_filter_equilibre(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, checkbox_values={"tag_equilibre": True})
        mock_service = MagicMock()
        recettes = [
            create_mock_recette(1, est_equilibre=True),
            create_mock_recette(2, est_equilibre=False),
        ]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_filter_congelable(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, checkbox_values={"tag_congelable": True})
        mock_service = MagicMock()
        recettes = [
            create_mock_recette(1, congelable=True),
            create_mock_recette(2, congelable=False),
        ]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_st.success.assert_called()


@pytest.mark.unit
class TestRenderListeDisplay:
    """Tests pour l'affichage des recettes."""

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_display_with_image_url(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        recette = create_mock_recette(1, url_image="https://example.com/img.jpg")
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert mock_st.markdown.called

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_display_without_image(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        recette = create_mock_recette(1, url_image=None)
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert mock_st.markdown.called

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_display_with_long_description(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        long_desc = "A" * 300
        recette = create_mock_recette(1, description=long_desc)
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert mock_st.markdown.called

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_display_without_description(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        recette = create_mock_recette(1, description=None)
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert mock_st.markdown.called

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_display_without_calories(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        recette = create_mock_recette(1, calories=None)
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert mock_st.markdown.called

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_display_difficulty_levels(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        recettes = [
            create_mock_recette(1, difficulte="facile"),
            create_mock_recette(2, difficulte="moyen"),
            create_mock_recette(3, difficulte="difficile"),
        ]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert mock_st.markdown.called


@pytest.mark.unit
class TestRenderListeBadges:
    """Tests pour les badges."""

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_display_all_badges(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        recette = create_mock_recette(
            1,
            est_bio=True,
            est_local=True,
            est_rapide=True,
            est_equilibre=True,
            congelable=True,
        )
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert mock_st.markdown.called

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_display_with_robots_compatibles(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        recette = create_mock_recette(
            1,
            robots_compatibles=["Cookeo", "Monsieur Cuisine", "Airfryer", "Multicooker"],
        )
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert mock_st.markdown.called

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_display_with_unknown_robot(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        recette = create_mock_recette(1, robots_compatibles=["Unknown Robot"])
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert mock_st.markdown.called


@pytest.mark.unit
class TestRenderListeActions:
    """Tests pour les actions (boutons)."""

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_click_voir_details(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, button_clicked="detail_1")
        mock_service = MagicMock()
        recette = create_mock_recette(1)
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert mock_st.session_state.get("detail_recette_id") == 1
        # OK

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_click_supprimer_confirm(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, button_clicked="btn_del_oui_1")
        mock_service = MagicMock()
        mock_service.delete.return_value = True
        recette = create_mock_recette(1)
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_service.delete.assert_called_with(1)
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_click_supprimer_failed(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, button_clicked="btn_del_oui_1")
        mock_service = MagicMock()
        mock_service.delete.return_value = False
        recette = create_mock_recette(1)
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_service.delete.assert_called()
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_click_supprimer_exception(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, button_clicked="btn_del_oui_1")
        mock_service = MagicMock()
        mock_service.delete.side_effect = Exception("Erreur DB")
        recette = create_mock_recette(1)
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_click_annuler_suppression(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, button_clicked="btn_del_non_1")
        mock_service = MagicMock()
        recette = create_mock_recette(1)
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        # OK


@pytest.mark.unit
class TestRenderListePagination:
    """Tests pour la pagination."""

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_pagination_next_page(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(
            mock_st,
            session_data={"recettes_page": 0, "recettes_page_size": 6},
            page_size=6,
            button_clicked=None,
        )
        mock_service = MagicMock()
        recettes = [create_mock_recette(i) for i in range(6)]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        # Pagination next button rendered
        # OK

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_pagination_previous_page(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(
            mock_st,
            session_data={"recettes_page": 1, "recettes_page_size": 6},
            page_size=6,
            button_clicked=None,
        )
        mock_service = MagicMock()
        recettes = [create_mock_recette(i) for i in range(6)]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        # Pagination previous button rendered

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_pagination_page_overflow_adjusted(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(
            mock_st,
            session_data={"recettes_page": 10, "recettes_page_size": 9},
            page_size=9,
        )
        mock_service = MagicMock()
        recettes = [create_mock_recette(i) for i in range(3)]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert mock_st.session_state.recettes_page == 0


@pytest.mark.unit
class TestRenderListeSessionState:
    """Tests pour l'initialisation du session_state."""

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_init_session_state_page(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        mock_st.session_state = SessionStateMock({"recettes_page_size": 9})
        setup_mock_st(mock_st, session_data={"recettes_page_size": 9})
        if "recettes_page" in mock_st.session_state:
            del mock_st.session_state["recettes_page"]

        mock_service = MagicMock()
        mock_service.search_advanced.return_value = []
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert "recettes_page" in mock_st.session_state

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_init_session_state_page_size(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        mock_st.session_state = SessionStateMock({"recettes_page": 0})
        setup_mock_st(mock_st, session_data={"recettes_page": 0})
        if "recettes_page_size" in mock_st.session_state:
            del mock_st.session_state["recettes_page_size"]

        mock_service = MagicMock()
        mock_service.search_advanced.return_value = []
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert "recettes_page_size" in mock_st.session_state


@pytest.mark.unit
class TestRenderListeEmptyResults:
    """Tests pour resultats vides."""

    @patch("src.modules.cuisine.recettes.liste.etat_vide")
    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_no_recettes_found(self, mock_st, mock_svc_factory, mock_etat_vide) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        mock_service.search_advanced.return_value = []
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_etat_vide.assert_called()


@pytest.mark.unit
class TestRenderListePageSizes:
    """Tests pour differentes tailles de page."""

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_page_size_6(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, page_size=6)
        mock_service = MagicMock()
        mock_service.search_advanced.return_value = [create_mock_recette(i) for i in range(10)]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert mock_st.session_state.recettes_page_size == 6

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_page_size_12(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, page_size=12)
        mock_service = MagicMock()
        mock_service.search_advanced.return_value = [create_mock_recette(i) for i in range(20)]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert mock_st.session_state.recettes_page_size == 12


@pytest.mark.unit
class TestRenderListeEdgeCases:
    """Tests pour cas limites."""

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_filter_nom_empty_whitespace(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, nom_filter="   ")
        mock_service = MagicMock()
        mock_service.search_advanced.return_value = [create_mock_recette()]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_description_truncate_no_space(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        long_desc = "A" * 160 + " " + "B" * 100
        recette = create_mock_recette(1, description=long_desc)
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert mock_st.markdown.called

    @patch("src.modules.cuisine.recettes.liste.etat_vide")
    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_recette_score_bio_none(self, mock_st, mock_svc_factory, mock_etat_vide) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, min_score_bio=20)
        mock_service = MagicMock()
        recette = create_mock_recette(1, score_bio=None)
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_etat_vide.assert_called()

    @patch("src.modules.cuisine.recettes.liste.etat_vide")
    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_recette_score_local_none(self, mock_st, mock_svc_factory, mock_etat_vide) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st, min_score_local=20)
        mock_service = MagicMock()
        recette = create_mock_recette(1, score_local=None)
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_etat_vide.assert_called()

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_difficulty_unknown(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        recette = create_mock_recette(1, difficulte="expert")
        mock_service.search_advanced.return_value = [recette]
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert mock_st.markdown.called

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_combined_robot_filters(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(
            mock_st,
            checkbox_values={"robot_cookeo": True, "robot_mc": True},
        )
        mock_service = MagicMock()
        recettes = [
            create_mock_recette(1, compatible_cookeo=True, compatible_monsieur_cuisine=True),
            create_mock_recette(2, compatible_cookeo=True, compatible_monsieur_cuisine=False),
            create_mock_recette(3, compatible_cookeo=False, compatible_monsieur_cuisine=True),
        ]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        mock_st.success.assert_called()


@pytest.mark.unit
class TestRenderListeMultipleRecettes:
    """Tests avec plusieurs recettes pour couvrir grid display."""

    @patch("src.modules.cuisine.recettes.liste.obtenir_service_recettes")
    @patch("src.modules.cuisine.recettes.liste.st")
    def test_display_grid_3_columns(self, mock_st, mock_svc_factory) -> None:
        from src.modules.cuisine.recettes.liste import afficher_liste

        setup_mock_st(mock_st)
        mock_service = MagicMock()
        recettes = [create_mock_recette(i, nom=f"Recette {i}") for i in range(5)]
        mock_service.search_advanced.return_value = recettes
        mock_svc_factory.return_value = mock_service
        afficher_liste()
        assert mock_st.markdown.called
        mock_st.success.assert_called()
