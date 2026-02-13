"""
Tests unitaires pour src/ui/layout/sidebar.py
"""

from unittest.mock import MagicMock, patch


class TestModulesMenu:
    """Tests pour MODULES_MENU."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.layout.sidebar import MODULES_MENU

        assert MODULES_MENU is not None

    def test_menu_structure(self):
        """Test structure du menu."""
        from src.ui.layout.sidebar import MODULES_MENU

        assert "ðŸ  Accueil" in MODULES_MENU
        assert "ðŸ³ Cuisine" in MODULES_MENU
        assert "ðŸ‘¨â€ðŸ‘©â€ðŸ‘§â€ðŸ‘¦ Famille" in MODULES_MENU

    def test_menu_values(self):
        """Test valeurs du menu."""
        from src.ui.layout.sidebar import MODULES_MENU

        assert MODULES_MENU["ðŸ  Accueil"] == "accueil"
        assert isinstance(MODULES_MENU["ðŸ³ Cuisine"], dict)

    def test_modules_menu_valid_values(self):
        """Test que toutes les valeurs du menu sont valides."""
        from src.ui.layout.sidebar import MODULES_MENU

        def check_values(menu):
            for label, value in menu.items():
                if isinstance(value, dict):
                    check_values(value)
                elif value is not None:
                    assert isinstance(value, str), f"Invalid value for {label}"

        check_values(MODULES_MENU)


class TestAfficherSidebar:
    """Tests pour afficher_sidebar()."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.layout.sidebar import afficher_sidebar

        assert afficher_sidebar is not None

    @patch("src.ui.layout.sidebar._rendre_menu")
    @patch("src.ui.layout.sidebar.st")
    @patch("src.ui.layout.sidebar.afficher_stats_chargement_differe")
    @patch("src.ui.layout.sidebar.obtenir_etat")
    @patch("src.ui.layout.sidebar.GestionnaireEtat")
    def test_afficher_sidebar_renders(self, mock_gest, mock_etat, mock_stats, mock_st, mock_menu):
        """Test que la sidebar se rend."""
        from src.ui.layout.sidebar import afficher_sidebar

        mock_etat.return_value = MagicMock(module_actuel="accueil", mode_debug=False)
        mock_gest.obtenir_fil_ariane_navigation.return_value = ["Accueil"]

        # Configure sidebar as context manager
        sidebar_mock = MagicMock()
        mock_st.sidebar.__enter__ = MagicMock(return_value=sidebar_mock)
        mock_st.sidebar.__exit__ = MagicMock(return_value=None)
        mock_st.checkbox.return_value = False

        afficher_sidebar()

        mock_st.title.assert_called()

    @patch("src.ui.layout.sidebar._rendre_menu")
    @patch("src.ui.layout.sidebar.st")
    @patch("src.ui.layout.sidebar.afficher_stats_chargement_differe")
    @patch("src.ui.layout.sidebar.obtenir_etat")
    @patch("src.ui.layout.sidebar.GestionnaireEtat")
    def test_sidebar_fil_ariane(self, mock_gest, mock_etat, mock_stats, mock_st, mock_menu):
        """Test fil d'Ariane."""
        from src.ui.layout.sidebar import afficher_sidebar

        mock_etat.return_value = MagicMock(module_actuel="cuisine.recettes", mode_debug=False)
        mock_gest.obtenir_fil_ariane_navigation.return_value = ["Accueil", "Cuisine", "Recettes"]

        sidebar_mock = MagicMock()
        mock_st.sidebar.__enter__ = MagicMock(return_value=sidebar_mock)
        mock_st.sidebar.__exit__ = MagicMock(return_value=None)
        mock_st.button.return_value = False
        mock_st.checkbox.return_value = False

        afficher_sidebar()

        mock_st.caption.assert_called()


class TestRendreMenu:
    """Tests pour _rendre_menu()."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.layout.sidebar import _rendre_menu

        assert _rendre_menu is not None

    @patch("src.ui.layout.sidebar.st")
    def test_rendre_menu_simple(self, mock_st):
        """Test rendu menu simple."""
        from src.ui.layout.sidebar import _rendre_menu

        etat = MagicMock(module_actuel="accueil")
        menu = {"ðŸ  Accueil": "accueil"}
        mock_st.button.return_value = False

        _rendre_menu(menu, etat)

        mock_st.button.assert_called()

    @patch("src.ui.layout.sidebar.st")
    def test_rendre_menu_submenu(self, mock_st):
        """Test rendu sous-menu."""
        from src.ui.layout.sidebar import _rendre_menu

        etat = MagicMock(module_actuel="cuisine.recettes")
        menu = {"ðŸ³ Cuisine": {"ðŸ“š Recettes": "cuisine.recettes"}}
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock()
        mock_st.button.return_value = False

        _rendre_menu(menu, etat)

        mock_st.expander.assert_called()

    @patch("src.ui.layout.sidebar.GestionnaireEtat")
    @patch("src.ui.layout.sidebar.st")
    def test_rendre_menu_separator(self, mock_st, mock_gest):
        """Test rendu séparateur dans menu."""
        from src.ui.layout.sidebar import _rendre_menu

        etat = MagicMock(module_actuel="accueil")
        menu = {"ðŸ³ Cuisine": {"â”€â”€â”€â”€â”€â”€â”€": None, "ðŸ“š Recettes": "cuisine.recettes"}}
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock()
        mock_st.button.return_value = False

        _rendre_menu(menu, etat)

        mock_st.divider.assert_called()

    @patch("src.ui.layout.sidebar.GestionnaireEtat")
    @patch("src.ui.layout.sidebar.st")
    def test_rendre_menu_click_navigation(self, mock_st, mock_gest):
        """Test clic sur menu déclenche navigation."""
        from src.ui.layout.sidebar import _rendre_menu

        etat = MagicMock(module_actuel="accueil")
        menu = {"ðŸ“š Recettes": "cuisine.recettes"}
        mock_st.button.return_value = True  # Simule un clic

        try:
            _rendre_menu(menu, etat)
        except Exception:
            pass  # st.rerun() peut lever une exception

        mock_gest.naviguer_vers.assert_called_with("cuisine.recettes")

    @patch("src.ui.layout.sidebar.GestionnaireEtat")
    @patch("src.ui.layout.sidebar.st")
    def test_rendre_menu_submenu_click(self, mock_st, mock_gest):
        """Test clic sur sous-menu."""
        from src.ui.layout.sidebar import _rendre_menu

        etat = MagicMock(module_actuel="accueil")
        menu = {"ðŸ³ Cuisine": {"ðŸ“š Recettes": "cuisine.recettes"}}
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock()
        mock_st.button.return_value = True  # Simule clic

        try:
            _rendre_menu(menu, etat)
        except Exception:
            pass

        mock_gest.naviguer_vers.assert_called()


class TestAfficherSidebarInteractions:
    """Tests interaction sidebar."""

    @patch("src.ui.layout.sidebar.Cache")
    @patch("src.ui.layout.sidebar.ChargeurModuleDiffere")
    @patch("src.ui.layout.sidebar._rendre_menu")
    @patch("src.ui.layout.sidebar.st")
    @patch("src.ui.layout.sidebar.afficher_stats_chargement_differe")
    @patch("src.ui.layout.sidebar.obtenir_etat")
    @patch("src.ui.layout.sidebar.GestionnaireEtat")
    def test_sidebar_debug_mode(
        self, mock_gest, mock_etat, mock_stats, mock_st, mock_menu, mock_loader, mock_cache
    ):
        """Test mode debug activé."""
        from src.ui.layout.sidebar import afficher_sidebar

        mock_etat.return_value = MagicMock(module_actuel="accueil", mode_debug=True)
        mock_gest.obtenir_fil_ariane_navigation.return_value = ["Accueil"]
        mock_gest.obtenir_resume_etat.return_value = {"test": "data"}

        mock_st.sidebar.__enter__ = MagicMock()
        mock_st.sidebar.__exit__ = MagicMock()
        mock_st.checkbox.return_value = True  # Debug activé
        mock_st.button.return_value = False  # Reset pas cliqué
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock()

        afficher_sidebar()

        mock_st.checkbox.assert_called()
        mock_st.json.assert_called()

    @patch("src.ui.layout.sidebar.Cache")
    @patch("src.ui.layout.sidebar.ChargeurModuleDiffere")
    @patch("src.ui.layout.sidebar._rendre_menu")
    @patch("src.ui.layout.sidebar.st")
    @patch("src.ui.layout.sidebar.afficher_stats_chargement_differe")
    @patch("src.ui.layout.sidebar.obtenir_etat")
    @patch("src.ui.layout.sidebar.GestionnaireEtat")
    def test_sidebar_reset_click(
        self, mock_gest, mock_etat, mock_stats, mock_st, mock_menu, mock_loader, mock_cache
    ):
        """Test clic sur Reset."""
        from src.ui.layout.sidebar import afficher_sidebar

        mock_etat.return_value = MagicMock(module_actuel="accueil", mode_debug=True)
        mock_gest.obtenir_fil_ariane_navigation.return_value = [
            "Accueil"
        ]  # 1 seul élément = pas de Retour
        mock_gest.obtenir_resume_etat.return_value = {}

        mock_st.sidebar.__enter__ = MagicMock()
        mock_st.sidebar.__exit__ = MagicMock()
        mock_st.checkbox.return_value = True
        mock_st.button.return_value = True  # Reset cliqué
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock()

        try:
            afficher_sidebar()
        except Exception:
            pass

        mock_gest.reinitialiser.assert_called()
        mock_cache.vider.assert_called()

    @patch("src.ui.layout.sidebar._rendre_menu")
    @patch("src.ui.layout.sidebar.st")
    @patch("src.ui.layout.sidebar.afficher_stats_chargement_differe")
    @patch("src.ui.layout.sidebar.obtenir_etat")
    @patch("src.ui.layout.sidebar.GestionnaireEtat")
    def test_sidebar_retour_click(self, mock_gest, mock_etat, mock_stats, mock_st, mock_menu):
        """Test clic sur Retour dans fil d'Ariane."""
        from src.ui.layout.sidebar import afficher_sidebar

        mock_etat.return_value = MagicMock(module_actuel="cuisine.recettes", mode_debug=False)
        mock_gest.obtenir_fil_ariane_navigation.return_value = ["Accueil", "Cuisine", "Recettes"]

        mock_st.sidebar.__enter__ = MagicMock()
        mock_st.sidebar.__exit__ = MagicMock()
        mock_st.button.return_value = True  # Retour cliqué en premier
        mock_st.checkbox.return_value = False

        try:
            afficher_sidebar()
        except Exception:
            pass

        mock_gest.revenir.assert_called()
