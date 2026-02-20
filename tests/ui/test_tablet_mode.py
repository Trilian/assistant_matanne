"""
Tests complets pour src/ui/tablet_mode.py
Couverture cible: >80%
"""

from unittest.mock import MagicMock, patch

# ═══════════════════════════════════════════════════════════
# TABLET MODE ENUM
# ═══════════════════════════════════════════════════════════


class TestModeTabletteEnum:
    """Tests pour ModeTablette enum."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet import ModeTablette

        assert ModeTablette is not None

    def test_values(self):
        """Test les valeurs de l'enum."""
        from src.ui.tablet import ModeTablette

        assert ModeTablette.NORMAL.value == "normal"
        assert ModeTablette.TABLETTE.value == "tablette"
        assert ModeTablette.CUISINE.value == "cuisine"

    def test_str_enum(self):
        """Test que c'est un str enum."""
        from src.ui.tablet import ModeTablette

        assert isinstance(ModeTablette.NORMAL, str)
        assert ModeTablette.NORMAL == "normal"


# ═══════════════════════════════════════════════════════════
# GET/SET TABLET MODE
# ═══════════════════════════════════════════════════════════


class TestGetSetModeTablette:
    """Tests pour get/set tablet mode."""

    @patch("streamlit.session_state", {})
    def test_get_default(self):
        """Test get avec valeur par défaut."""
        from src.ui.tablet import ModeTablette, obtenir_mode_tablette

        result = obtenir_mode_tablette()
        assert result == ModeTablette.NORMAL

    @patch("streamlit.session_state", {"mode_tablette": "tablette"})
    def test_get_from_string(self):
        """Test get avec string stockée."""
        from src.ui.tablet import ModeTablette, obtenir_mode_tablette

        result = obtenir_mode_tablette()
        assert result == ModeTablette.TABLETTE

    @patch("streamlit.session_state", {})
    def test_set_mode(self):
        """Test set mode."""
        import streamlit as st

        from src.ui.tablet import ModeTablette, definir_mode_tablette

        definir_mode_tablette(ModeTablette.CUISINE)

        assert st.session_state["mode_tablette"] == ModeTablette.CUISINE


# ═══════════════════════════════════════════════════════════
# APPLY/CLOSE TABLET MODE
# ═══════════════════════════════════════════════════════════


class TestApplyModeTablette:
    """Tests pour appliquer_mode_tablette."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet import appliquer_mode_tablette

        assert appliquer_mode_tablette is not None

    @patch("streamlit.session_state", {})
    @patch("streamlit.markdown")
    def test_apply_normal_mode(self, mock_md):
        """Test apply en mode normal."""
        from src.ui.tablet import appliquer_mode_tablette

        appliquer_mode_tablette()

        # CSS de base est inclus
        mock_md.assert_called()

    @patch("streamlit.session_state", {"mode_tablette": "tablette"})
    @patch("streamlit.markdown")
    def test_appliquer_mode_tablette(self, mock_md):
        """Test apply en mode tablette."""
        from src.ui.tablet import appliquer_mode_tablette

        appliquer_mode_tablette()

        # Vérifie que tablet-mode div est ajouté
        calls = [str(call) for call in mock_md.call_args_list]
        assert any("tablet-mode" in call for call in calls)

    @patch("streamlit.session_state", {"mode_tablette": "cuisine"})
    @patch("streamlit.markdown")
    def test_appliquer_mode_cuisine(self, mock_md):
        """Test apply en mode cuisine."""
        from src.ui.tablet import appliquer_mode_tablette

        appliquer_mode_tablette()

        # Vérifie que kitchen-mode div est ajouté
        calls = [str(call) for call in mock_md.call_args_list]
        assert any("kitchen-mode" in call for call in calls)


class TestCloseModeTablette:
    """Tests pour fermer_mode_tablette."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet import fermer_mode_tablette

        assert fermer_mode_tablette is not None

    @patch("streamlit.session_state", {})
    @patch("streamlit.markdown")
    def test_close_normal(self, mock_md):
        """Test close en mode normal - ne fait rien."""
        from src.ui.tablet import fermer_mode_tablette

        fermer_mode_tablette()

        mock_md.assert_not_called()

    @patch("streamlit.session_state", {"mode_tablette": "tablette"})
    @patch("streamlit.components.v1.html")
    def test_fermer_tablette(self, mock_html):
        """Test close en mode tablette."""
        from src.ui.tablet import fermer_mode_tablette

        fermer_mode_tablette()

        mock_html.assert_called_once()
        call_args = mock_html.call_args
        assert "classList.remove" in call_args[0][0]


# ═══════════════════════════════════════════════════════════
# TABLET BUTTON
# ═══════════════════════════════════════════════════════════


class TestTabletButton:
    """Tests pour bouton_tablette."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet import bouton_tablette

        assert bouton_tablette is not None

    @patch("streamlit.button", return_value=True)
    def test_basic_button(self, mock_btn):
        """Test bouton basique."""
        from src.ui.tablet import bouton_tablette

        result = bouton_tablette("Cliquer", key="test")

        assert result is True
        mock_btn.assert_called_once()

    @patch("streamlit.button", return_value=False)
    def test_button_with_icon(self, mock_btn):
        """Test bouton avec icône."""
        from src.ui.tablet import bouton_tablette

        bouton_tablette("Action", key="icon_test", icon="ðŸ”¥")

        # Vérifie que l'icône est dans le label
        call_args = mock_btn.call_args
        assert "ðŸ”¥" in call_args[0][0]

    @patch("streamlit.button", return_value=False)
    def test_button_primary(self, mock_btn):
        """Test bouton primary."""
        from src.ui.tablet import bouton_tablette

        bouton_tablette("Primary", key="primary_test", type="primary")

        call_kwargs = mock_btn.call_args[1]
        assert call_kwargs.get("type") == "primary"

    @patch("streamlit.button", return_value=False)
    def test_button_danger(self, mock_btn):
        """Test bouton danger."""
        from src.ui.tablet import bouton_tablette

        bouton_tablette("Delete", key="danger_test", type="danger")

        call_kwargs = mock_btn.call_args[1]
        assert "help" in call_kwargs


# ═══════════════════════════════════════════════════════════
# TABLET SELECT GRID
# ═══════════════════════════════════════════════════════════


class TestTabletSelectGrid:
    """Tests pour grille_selection_tablette."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet import grille_selection_tablette

        assert grille_selection_tablette is not None

    @patch("streamlit.session_state", {})
    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=False)
    def test_grid_no_selection(self, mock_btn, mock_cols):
        """Test grille sans sélection."""
        from src.ui.tablet import grille_selection_tablette

        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        options = [
            {"value": "a", "label": "Option A", "icon": "ðŸ…°ï¸"},
            {"value": "b", "label": "Option B", "icon": "ðŸ…±ï¸"},
        ]

        result = grille_selection_tablette(options, key="grid_test")

        assert result is None

    @patch("streamlit.session_state", {"grid_sel_selected": "existing"})
    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=False)
    def test_grid_with_existing_selection(self, mock_btn, mock_cols):
        """Test grille avec sélection existante."""
        from src.ui.tablet import grille_selection_tablette

        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        options = [{"value": "existing", "label": "Ex", "icon": "âœ…"}]

        result = grille_selection_tablette(options, key="grid_sel")

        assert result == "existing"


# ═══════════════════════════════════════════════════════════
# TABLET NUMBER INPUT
# ═══════════════════════════════════════════════════════════


class TestTabletNumberInput:
    """Tests pour saisie_nombre_tablette."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet import saisie_nombre_tablette

        assert saisie_nombre_tablette is not None

    @patch("streamlit.session_state", {})
    @patch("streamlit.write")
    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.markdown")
    def test_number_input_default(self, mock_md, mock_btn, mock_cols, mock_write):
        """Test input avec valeur par défaut."""
        from src.ui.tablet import saisie_nombre_tablette

        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        result = saisie_nombre_tablette("Quantité", key="num_test", default=5)

        assert result == 5

    @patch("streamlit.session_state", {"num_minus_value": 10})
    @patch("streamlit.write")
    @patch("streamlit.columns")
    @patch("streamlit.button")
    @patch("streamlit.markdown")
    @patch("streamlit.rerun")
    def test_number_input_minus(self, mock_rerun, mock_md, mock_btn, mock_cols, mock_write):
        """Test bouton moins."""
        import streamlit as st

        from src.ui.tablet import saisie_nombre_tablette

        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        # Premier bouton (minus) retourne True
        mock_btn.side_effect = [True, False]

        try:
            saisie_nombre_tablette("Test", key="num_minus")
        except Exception:
            pass

        # La valeur devrait diminuer
        assert st.session_state.get("num_minus_value") == 9

    @patch("streamlit.session_state", {"num_plus_value": 5})
    @patch("streamlit.write")
    @patch("streamlit.columns")
    @patch("streamlit.button")
    @patch("streamlit.markdown")
    @patch("streamlit.rerun")
    def test_number_input_plus(self, mock_rerun, mock_md, mock_btn, mock_cols, mock_write):
        """Test bouton plus."""
        import streamlit as st

        from src.ui.tablet import saisie_nombre_tablette

        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        # Deuxième bouton (plus) retourne True
        mock_btn.side_effect = [False, True]

        try:
            saisie_nombre_tablette("Test", key="num_plus", max_value=10)
        except Exception:
            pass

        assert st.session_state.get("num_plus_value") == 6


# ═══════════════════════════════════════════════════════════
# TABLET CHECKLIST
# ═══════════════════════════════════════════════════════════


class TestTabletChecklist:
    """Tests pour liste_cases_tablette."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet import liste_cases_tablette

        assert liste_cases_tablette is not None

    @patch("streamlit.session_state", {})
    @patch("streamlit.button", return_value=False)
    def test_checklist_empty(self, mock_btn):
        """Test checklist vide."""
        from src.ui.tablet import liste_cases_tablette

        result = liste_cases_tablette([], key="check_empty")

        assert result == {}

    @patch("streamlit.session_state", {})
    @patch("streamlit.button", return_value=False)
    def test_checklist_unchecked(self, mock_btn):
        """Test checklist non cochée."""
        from src.ui.tablet import liste_cases_tablette

        items = ["Item 1", "Item 2", "Item 3"]
        result = liste_cases_tablette(items, key="check_test")

        assert all(not v for v in result.values())

    @patch("streamlit.session_state", {"check_cb_checked": {"A": True, "B": False}})
    @patch("streamlit.button", return_value=False)
    def test_checklist_with_callback(self, mock_btn):
        """Test checklist avec callback."""
        from src.ui.tablet import liste_cases_tablette

        callback = MagicMock()
        items = ["A", "B"]

        result = liste_cases_tablette(items, key="check_cb", on_check=callback)

        assert result["A"] is True
        assert result["B"] is False


# ═══════════════════════════════════════════════════════════
# RENDER MODE SELECTOR
# ═══════════════════════════════════════════════════════════


class TestRenderModeSelector:
    """Tests pour afficher_selecteur_mode."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet import afficher_selecteur_mode

        assert afficher_selecteur_mode is not None

    @patch("streamlit.session_state", {})
    @patch("streamlit.sidebar")
    @patch("streamlit.selectbox")
    @patch("streamlit.markdown")
    def test_render_normal_mode(self, mock_md, mock_select, mock_sidebar):
        """Test render en mode normal."""
        from src.ui.tablet import ModeTablette, afficher_selecteur_mode

        mock_sidebar.__enter__ = MagicMock()
        mock_sidebar.__exit__ = MagicMock()
        mock_select.return_value = ModeTablette.NORMAL

        afficher_selecteur_mode()

        mock_select.assert_called_once()

    @patch("streamlit.session_state", {"mode_tablette": "cuisine"})
    @patch("streamlit.sidebar")
    @patch("streamlit.selectbox")
    @patch("streamlit.markdown")
    @patch("streamlit.info")
    def test_render_kitchen_mode(self, mock_info, mock_md, mock_select, mock_sidebar):
        """Test render en mode cuisine - affiche info."""
        from src.ui.tablet import ModeTablette, afficher_selecteur_mode

        mock_sidebar.__enter__ = MagicMock()
        mock_sidebar.__exit__ = MagicMock()
        mock_select.return_value = ModeTablette.CUISINE

        afficher_selecteur_mode()

        # Info devrait être affiché en mode cuisine
        mock_info.assert_called_once()

    @patch("streamlit.session_state", {"mode_tablette": "normal"})
    @patch("streamlit.sidebar")
    @patch("streamlit.selectbox")
    @patch("streamlit.markdown")
    @patch("streamlit.rerun")
    def test_render_mode_change(self, mock_rerun, mock_md, mock_select, mock_sidebar):
        """Test changement de mode déclenche rerun."""
        from src.ui.tablet import ModeTablette, afficher_selecteur_mode

        mock_sidebar.__enter__ = MagicMock()
        mock_sidebar.__exit__ = MagicMock()
        mock_select.return_value = ModeTablette.TABLETTE  # Différent du mode actuel

        try:
            afficher_selecteur_mode()
        except Exception:
            pass

        mock_rerun.assert_called_once()


# ═══════════════════════════════════════════════════════════
# RENDER KITCHEN RECIPE VIEW
# ═══════════════════════════════════════════════════════════


class TestRenderKitchenRecipeView:
    """Tests pour afficher_vue_recette_cuisine."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet import afficher_vue_recette_cuisine

        assert afficher_vue_recette_cuisine is not None

    @patch("streamlit.session_state", {})
    @patch("streamlit.markdown")
    @patch("streamlit.tabs")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.columns")
    @patch("streamlit.progress")
    def test_recipe_start_screen(self, mock_prog, mock_cols, mock_btn, mock_tabs, mock_md):
        """Test écran de démarrage recette."""
        from src.ui.tablet import afficher_vue_recette_cuisine

        mock_tabs.return_value = [MagicMock(), MagicMock()]
        for tab in mock_tabs.return_value:
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock()

        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        recette = {
            "nom": "Tarte aux pommes",
            "temps_preparation": 20,
            "temps_cuisson": 40,
            "instructions": ["Étape 1", "Étape 2"],
            "ingredients": ["Pommes", "Sucre"],
        }

        afficher_vue_recette_cuisine(recette, cle="test_recipe")

        mock_md.assert_called()

    @patch("streamlit.session_state", {"test_etape": 1})
    @patch("streamlit.markdown")
    @patch("streamlit.tabs")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.columns")
    @patch("streamlit.progress")
    @patch("streamlit.checkbox")
    def test_recipe_step_view(self, mock_check, mock_prog, mock_cols, mock_btn, mock_tabs, mock_md):
        """Test affichage étape de recette."""
        import streamlit as st

        from src.ui.tablet import afficher_vue_recette_cuisine

        st.session_state["test_etape"] = 1

        mock_tabs.return_value = [MagicMock(), MagicMock()]
        for tab in mock_tabs.return_value:
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock()

        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        recette = {
            "nom": "Test",
            "instructions": ["Mélanger", "Cuire"],
            "ingredients": [{"quantite": "100", "unite": "g", "nom": "Farine"}],
        }

        afficher_vue_recette_cuisine(recette, cle="test")

        mock_prog.assert_called()

    @patch("streamlit.session_state", {"test_fin_etape": 3})
    @patch("streamlit.markdown")
    @patch("streamlit.tabs")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.columns")
    @patch("streamlit.balloons")
    def test_recipe_end_screen(self, mock_balloons, mock_cols, mock_btn, mock_tabs, mock_md):
        """Test écran de fin de recette."""
        import streamlit as st

        from src.ui.tablet import afficher_vue_recette_cuisine

        st.session_state["test_fin_etape"] = 3

        mock_tabs.return_value = [MagicMock(), MagicMock()]
        for tab in mock_tabs.return_value:
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock()

        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        recette = {
            "nom": "Test",
            "instructions": ["A", "B"],  # 2 étapes, step=3 = fin
        }

        afficher_vue_recette_cuisine(recette, cle="test_fin")

        mock_balloons.assert_called_once()

    @patch("streamlit.session_state", {"test_timer_etape": 1})
    @patch("streamlit.markdown")
    @patch("streamlit.tabs")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.columns")
    @patch("streamlit.progress")
    @patch("streamlit.checkbox")
    @patch("streamlit.expander")
    def test_recipe_with_timer(
        self, mock_expander, mock_check, mock_prog, mock_cols, mock_btn, mock_tabs, mock_md
    ):
        """Test recette avec timer (TimerCuisine intégré)."""
        from src.ui.tablet import afficher_vue_recette_cuisine

        mock_tabs.return_value = [MagicMock(), MagicMock()]
        for tab in mock_tabs.return_value:
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock()

        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        mock_exp = MagicMock()
        mock_exp.__enter__ = MagicMock(return_value=mock_exp)
        mock_exp.__exit__ = MagicMock()
        mock_expander.return_value = mock_exp

        recette = {"nom": "Test", "instructions": ["Cuire"]}

        afficher_vue_recette_cuisine(recette, cle="test_timer")

        # L'expander timer doit être affiché
        mock_expander.assert_called()

    @patch("streamlit.session_state", {"nav_etape": 2})
    @patch("streamlit.markdown")
    @patch("streamlit.tabs")
    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.progress")
    @patch("streamlit.checkbox")
    @patch("streamlit.rerun")
    @patch("streamlit.expander")
    def test_recipe_navigation_prev(
        self,
        mock_expander,
        mock_rerun,
        mock_check,
        mock_prog,
        mock_cols,
        mock_btn,
        mock_tabs,
        mock_md,
    ):
        """Test navigation précédent."""
        import streamlit as st

        from src.ui.tablet import afficher_vue_recette_cuisine

        st.session_state["nav_etape"] = 2

        mock_tabs.return_value = [MagicMock(), MagicMock()]
        for tab in mock_tabs.return_value:
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock()

        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        mock_exp = MagicMock()
        mock_exp.__enter__ = MagicMock(return_value=mock_exp)
        mock_exp.__exit__ = MagicMock()
        mock_expander.return_value = mock_exp

        # Buttons: Précédent=True, Quitter=False, Suivant=False
        mock_btn.side_effect = [True, False, False]

        recette = {"nom": "Test", "instructions": ["A", "B", "C"]}

        try:
            afficher_vue_recette_cuisine(recette, cle="nav")
        except Exception:
            pass

        assert st.session_state.get("nav_etape") == 1

    @patch("streamlit.session_state", {"start_etape": 0})
    @patch("streamlit.markdown")
    @patch("streamlit.tabs")
    @patch("streamlit.button")
    @patch("streamlit.columns")
    @patch("streamlit.metric")
    def test_recipe_start_button(self, mock_metric, mock_cols, mock_btn, mock_tabs, mock_md):
        """Test bouton commencer est affiché."""
        from src.ui.tablet import afficher_vue_recette_cuisine

        mock_tabs.return_value = [MagicMock(), MagicMock()]
        for tab in mock_tabs.return_value:
            tab.__enter__ = MagicMock(return_value=tab)
            tab.__exit__ = MagicMock()

        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        mock_btn.return_value = False  # Pas de clic

        recette = {"nom": "Test", "temps_preparation": 10, "instructions": ["A"]}

        afficher_vue_recette_cuisine(recette, cle="start")

        # Vérifie que button est appelé (écran d'accueil)
        mock_btn.assert_called()


# ═══════════════════════════════════════════════════════════
# INTEGRATION
# ═══════════════════════════════════════════════════════════


class TestModeTabletteIntegration:
    """Tests d'intégration."""

    def test_css_constants_exist(self):
        """Test que les constantes CSS existent."""
        from src.ui.tablet import CSS_TABLETTE

        assert CSS_TABLETTE is not None
        assert len(CSS_TABLETTE) > 100  # CSS substantiel

    def test_kitchen_css_exists(self):
        """Test que le CSS cuisine existe."""
        from src.ui.tablet import CSS_MODE_CUISINE

        assert CSS_MODE_CUISINE is not None

    def test_all_exports(self):
        """Test tous les exports principaux."""
        from src.ui.tablet import (
            CSS_MODE_CUISINE,
            CSS_TABLETTE,
            ModeTablette,
            afficher_selecteur_mode,
            afficher_vue_recette_cuisine,
            appliquer_mode_tablette,
            bouton_tablette,
            definir_mode_tablette,
            fermer_mode_tablette,
            grille_selection_tablette,
            liste_cases_tablette,
            obtenir_mode_tablette,
            saisie_nombre_tablette,
        )

        assert all(
            [
                ModeTablette,
                obtenir_mode_tablette,
                definir_mode_tablette,
                appliquer_mode_tablette,
                fermer_mode_tablette,
                bouton_tablette,
                grille_selection_tablette,
                saisie_nombre_tablette,
                liste_cases_tablette,
                afficher_vue_recette_cuisine,
                afficher_selecteur_mode,
                CSS_TABLETTE,
                CSS_MODE_CUISINE,
            ]
        )
