"""
Tests pour src/modules/maison/depenses/__init__.py

Tests complets pour le module Dépenses avec mocking Streamlit.
"""

from unittest.mock import MagicMock, patch

import pytest


class SessionStateMock(dict):
    """Mock de session_state Streamlit supportant dict et attributs"""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key) from None

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key) from None


class TestDepensesApp:
    """Tests pour app()"""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit"""
        with patch("src.modules.maison.depenses.st") as mock:
            mock.session_state = SessionStateMock()
            mock.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]
            yield mock

    @pytest.fixture
    def mock_crud(self):
        """Mock CRUD functions"""
        with patch("src.modules.maison.depenses.get_depense_by_id") as mock_get:
            mock_get.return_value = None
            yield mock_get

    @pytest.fixture
    def mock_components(self):
        """Mock des composants UI"""
        with (
            patch("src.modules.maison.depenses.afficher_stats_dashboard") as mock_stats,
            patch("src.modules.maison.depenses.afficher_onglet_mois") as mock_mois,
            patch("src.modules.maison.depenses.afficher_onglet_ajouter") as mock_ajouter,
            patch("src.modules.maison.depenses.afficher_onglet_analyse") as mock_analyse,
            patch("src.modules.maison.depenses.afficher_formulaire") as mock_formulaire,
        ):
            yield {
                "stats": mock_stats,
                "mois": mock_mois,
                "ajouter": mock_ajouter,
                "analyse": mock_analyse,
                "formulaire": mock_formulaire,
            }

    def test_app_affiche_titre(self, mock_st, mock_components):
        """Vérifie l'affichage du titre"""
        from src.modules.maison.depenses import app

        app()

        mock_st.title.assert_called_once()
        assert "Dépenses" in mock_st.title.call_args[0][0]

    def test_app_affiche_caption(self, mock_st, mock_components):
        """Vérifie l'affichage du caption"""
        from src.modules.maison.depenses import app

        app()

        mock_st.caption.assert_called_once()

    def test_app_cree_onglets(self, mock_st, mock_components):
        """Vérifie la création des 3 onglets"""
        from src.modules.maison.depenses import app

        app()

        mock_st.tabs.assert_called_once()
        tabs_labels = mock_st.tabs.call_args[0][0]
        assert len(tabs_labels) == 3

    def test_app_mode_edition_avec_depense(self, mock_st, mock_components):
        """Vérifie le mode édition avec dépense valide"""
        mock_st.session_state = {"edit_depense_id": 1}
        mock_depense = MagicMock()
        mock_depense.categorie = "electricite"

        with (
            patch("src.modules.maison.depenses.get_depense_by_id") as mock_get,
            patch("src.modules.maison.depenses.afficher_formulaire"),
            patch("src.modules.maison.depenses.CATEGORY_LABELS", {"electricite": "Électricité"}),
        ):
            mock_get.return_value = mock_depense
            mock_st.button.return_value = False

            from src.modules.maison.depenses import app

            app()

            mock_st.subheader.assert_called()

    def test_app_mode_edition_annuler(self, mock_st, mock_components):
        """Vérifie l'annulation du mode édition"""
        mock_st.session_state = SessionStateMock({"edit_depense_id": 1})
        mock_st.button.return_value = True

        with (
            patch("src.modules.maison.depenses.get_depense_by_id") as mock_get,
            patch("src.modules.maison.depenses.CATEGORY_LABELS", {"gaz": "Gaz"}),
            patch("src.modules.maison.depenses.rerun") as mock_rerun,
        ):
            mock_get.return_value = MagicMock(categorie="gaz")
            # rerun() should stop execution, simulate with exception
            mock_rerun.side_effect = SystemExit()

            from src.modules.maison.depenses import app

            with pytest.raises(SystemExit):
                app()

            mock_st.button.assert_called()
            mock_rerun.assert_called()

    def test_app_mode_edition_depense_introuvable(self, mock_st, mock_components):
        """Vérifie le comportement si dépense non trouvée"""
        mock_st.session_state = SessionStateMock({"edit_depense_id": 999})

        with patch("src.modules.maison.depenses.get_depense_by_id") as mock_get:
            mock_get.return_value = None

            from src.modules.maison.depenses import app

            app()

            # Doit continuer vers le dashboard
            mock_components["stats"].assert_called()


class TestDepensesExports:
    """Tests pour les exports du module"""

    def test_exports_crud(self):
        """Vérifie que les fonctions CRUD sont exportées"""
        from src.modules.maison.depenses import (
            create_depense,
            delete_depense,
            get_depense_by_id,
            get_depenses_annee,
            get_depenses_mois,
            get_historique_categorie,
            get_stats_globales,
            update_depense,
        )

        assert callable(create_depense)
        assert callable(delete_depense)
        assert callable(get_depense_by_id)
        assert callable(get_depenses_annee)
        assert callable(get_depenses_mois)
        assert callable(get_historique_categorie)
        assert callable(get_stats_globales)
        assert callable(update_depense)

    def test_exports_ui(self):
        """Vérifie que les composants UI sont exportés"""
        from src.modules.maison.depenses import (
            afficher_comparaison_mois,
            afficher_depense_card,
            afficher_formulaire,
            afficher_graphique_evolution,
            afficher_onglet_ajouter,
            afficher_onglet_analyse,
            afficher_onglet_mois,
            afficher_stats_dashboard,
        )

        assert callable(afficher_comparaison_mois)
        assert callable(afficher_depense_card)
        assert callable(afficher_formulaire)
        assert callable(afficher_graphique_evolution)
        assert callable(afficher_onglet_ajouter)
        assert callable(afficher_onglet_analyse)
        assert callable(afficher_onglet_mois)
        assert callable(afficher_stats_dashboard)

    def test_all_contains_expected(self):
        """Vérifie le contenu de __all__"""
        from src.modules.maison.depenses import __all__

        assert "app" in __all__
        assert "get_depenses_mois" in __all__
        assert "afficher_stats_dashboard" in __all__
