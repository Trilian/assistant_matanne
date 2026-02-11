"""
Tests complets pour src/ui/tablet_mode.py
Couverture cible: >80%
"""

import pytest
from unittest.mock import MagicMock, patch
from enum import Enum


# ═══════════════════════════════════════════════════════════
# TABLET MODE ENUM
# ═══════════════════════════════════════════════════════════


class TestTabletModeEnum:
    """Tests pour TabletMode enum."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet_mode import TabletMode
        assert TabletMode is not None

    def test_values(self):
        """Test les valeurs de l'enum."""
        from src.ui.tablet_mode import TabletMode
        
        assert TabletMode.NORMAL.value == "normal"
        assert TabletMode.TABLET.value == "tablet"
        assert TabletMode.KITCHEN.value == "kitchen"

    def test_str_enum(self):
        """Test que c'est un str enum."""
        from src.ui.tablet_mode import TabletMode
        
        assert isinstance(TabletMode.NORMAL, str)
        assert TabletMode.NORMAL == "normal"


# ═══════════════════════════════════════════════════════════
# GET/SET TABLET MODE
# ═══════════════════════════════════════════════════════════


class TestGetSetTabletMode:
    """Tests pour get/set tablet mode."""

    @patch("streamlit.session_state", {})
    def test_get_default(self):
        """Test get avec valeur par défaut."""
        from src.ui.tablet_mode import get_tablet_mode, TabletMode
        
        result = get_tablet_mode()
        assert result == TabletMode.NORMAL

    @patch("streamlit.session_state", {"tablet_mode": "tablet"})
    def test_get_from_string(self):
        """Test get avec string stockée."""
        from src.ui.tablet_mode import get_tablet_mode, TabletMode
        
        result = get_tablet_mode()
        assert result == TabletMode.TABLET

    @patch("streamlit.session_state", {})
    def test_set_mode(self):
        """Test set mode."""
        from src.ui.tablet_mode import set_tablet_mode, TabletMode
        import streamlit as st
        
        set_tablet_mode(TabletMode.KITCHEN)
        
        assert st.session_state["tablet_mode"] == TabletMode.KITCHEN


# ═══════════════════════════════════════════════════════════
# APPLY/CLOSE TABLET MODE
# ═══════════════════════════════════════════════════════════


class TestApplyTabletMode:
    """Tests pour apply_tablet_mode."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet_mode import apply_tablet_mode
        assert apply_tablet_mode is not None

    @patch("streamlit.session_state", {})
    @patch("streamlit.markdown")
    def test_apply_normal_mode(self, mock_md):
        """Test apply en mode normal."""
        from src.ui.tablet_mode import apply_tablet_mode
        
        apply_tablet_mode()
        
        # CSS de base est inclus
        mock_md.assert_called()

    @patch("streamlit.session_state", {"tablet_mode": "tablet"})
    @patch("streamlit.markdown")
    def test_apply_tablet_mode(self, mock_md):
        """Test apply en mode tablette."""
        from src.ui.tablet_mode import apply_tablet_mode
        
        apply_tablet_mode()
        
        # Vérifie que tablet-mode div est ajouté
        calls = [str(call) for call in mock_md.call_args_list]
        assert any("tablet-mode" in call for call in calls)

    @patch("streamlit.session_state", {"tablet_mode": "kitchen"})
    @patch("streamlit.markdown")
    def test_apply_kitchen_mode(self, mock_md):
        """Test apply en mode cuisine."""
        from src.ui.tablet_mode import apply_tablet_mode
        
        apply_tablet_mode()
        
        # Vérifie que kitchen-mode div est ajouté
        calls = [str(call) for call in mock_md.call_args_list]
        assert any("kitchen-mode" in call for call in calls)


class TestCloseTabletMode:
    """Tests pour close_tablet_mode."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet_mode import close_tablet_mode
        assert close_tablet_mode is not None

    @patch("streamlit.session_state", {})
    @patch("streamlit.markdown")
    def test_close_normal(self, mock_md):
        """Test close en mode normal - ne fait rien."""
        from src.ui.tablet_mode import close_tablet_mode
        
        close_tablet_mode()
        
        mock_md.assert_not_called()

    @patch("streamlit.session_state", {"tablet_mode": "tablet"})
    @patch("streamlit.markdown")
    def test_close_tablet(self, mock_md):
        """Test close en mode tablette."""
        from src.ui.tablet_mode import close_tablet_mode
        
        close_tablet_mode()
        
        mock_md.assert_called_once()
        assert "</div>" in mock_md.call_args[0][0]


# ═══════════════════════════════════════════════════════════
# TABLET BUTTON
# ═══════════════════════════════════════════════════════════


class TestTabletButton:
    """Tests pour tablet_button."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet_mode import tablet_button
        assert tablet_button is not None

    @patch("streamlit.button", return_value=True)
    def test_basic_button(self, mock_btn):
        """Test bouton basique."""
        from src.ui.tablet_mode import tablet_button
        
        result = tablet_button("Cliquer", key="test")
        
        assert result is True
        mock_btn.assert_called_once()

    @patch("streamlit.button", return_value=False)
    def test_button_with_icon(self, mock_btn):
        """Test bouton avec icône."""
        from src.ui.tablet_mode import tablet_button
        
        tablet_button("Action", key="icon_test", icon="🔥")
        
        # Vérifie que l'icône est dans le label
        call_args = mock_btn.call_args
        assert "🔥" in call_args[0][0]

    @patch("streamlit.button", return_value=False)
    def test_button_primary(self, mock_btn):
        """Test bouton primary."""
        from src.ui.tablet_mode import tablet_button
        
        tablet_button("Primary", key="primary_test", type="primary")
        
        call_kwargs = mock_btn.call_args[1]
        assert call_kwargs.get("type") == "primary"

    @patch("streamlit.button", return_value=False)
    def test_button_danger(self, mock_btn):
        """Test bouton danger."""
        from src.ui.tablet_mode import tablet_button
        
        tablet_button("Delete", key="danger_test", type="danger")
        
        call_kwargs = mock_btn.call_args[1]
        assert "help" in call_kwargs


# ═══════════════════════════════════════════════════════════
# TABLET SELECT GRID
# ═══════════════════════════════════════════════════════════


class TestTabletSelectGrid:
    """Tests pour tablet_select_grid."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet_mode import tablet_select_grid
        assert tablet_select_grid is not None

    @patch("streamlit.session_state", {})
    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=False)
    def test_grid_no_selection(self, mock_btn, mock_cols):
        """Test grille sans sélection."""
        from src.ui.tablet_mode import tablet_select_grid
        
        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()
        
        options = [
            {"value": "a", "label": "Option A", "icon": "🅰️"},
            {"value": "b", "label": "Option B", "icon": "🅱️"},
        ]
        
        result = tablet_select_grid(options, key="grid_test")
        
        assert result is None

    @patch("streamlit.session_state", {"grid_sel_selected": "existing"})
    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=False)
    def test_grid_with_existing_selection(self, mock_btn, mock_cols):
        """Test grille avec sélection existante."""
        from src.ui.tablet_mode import tablet_select_grid
        
        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()
        
        options = [{"value": "existing", "label": "Ex", "icon": "✅"}]
        
        result = tablet_select_grid(options, key="grid_sel")
        
        assert result == "existing"


# ═══════════════════════════════════════════════════════════
# TABLET NUMBER INPUT
# ═══════════════════════════════════════════════════════════


class TestTabletNumberInput:
    """Tests pour tablet_number_input."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet_mode import tablet_number_input
        assert tablet_number_input is not None

    @patch("streamlit.session_state", {})
    @patch("streamlit.write")
    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.markdown")
    def test_number_input_default(self, mock_md, mock_btn, mock_cols, mock_write):
        """Test input avec valeur par défaut."""
        from src.ui.tablet_mode import tablet_number_input
        
        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()
        
        result = tablet_number_input("Quantité", key="num_test", default=5)
        
        assert result == 5

    @patch("streamlit.session_state", {"num_minus_value": 10})
    @patch("streamlit.write")
    @patch("streamlit.columns")
    @patch("streamlit.button")
    @patch("streamlit.markdown")
    @patch("streamlit.rerun")
    def test_number_input_minus(self, mock_rerun, mock_md, mock_btn, mock_cols, mock_write):
        """Test bouton moins."""
        from src.ui.tablet_mode import tablet_number_input
        import streamlit as st
        
        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()
        
        # Premier bouton (minus) retourne True
        mock_btn.side_effect = [True, False]
        
        try:
            tablet_number_input("Test", key="num_minus")
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
        from src.ui.tablet_mode import tablet_number_input
        import streamlit as st
        
        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()
        
        # Deuxième bouton (plus) retourne True
        mock_btn.side_effect = [False, True]
        
        try:
            tablet_number_input("Test", key="num_plus", max_value=10)
        except Exception:
            pass
        
        assert st.session_state.get("num_plus_value") == 6


# ═══════════════════════════════════════════════════════════
# TABLET CHECKLIST
# ═══════════════════════════════════════════════════════════


class TestTabletChecklist:
    """Tests pour tablet_checklist."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet_mode import tablet_checklist
        assert tablet_checklist is not None

    @patch("streamlit.session_state", {})
    @patch("streamlit.button", return_value=False)
    def test_checklist_empty(self, mock_btn):
        """Test checklist vide."""
        from src.ui.tablet_mode import tablet_checklist
        
        result = tablet_checklist([], key="check_empty")
        
        assert result == {}

    @patch("streamlit.session_state", {})
    @patch("streamlit.button", return_value=False)
    def test_checklist_unchecked(self, mock_btn):
        """Test checklist non cochée."""
        from src.ui.tablet_mode import tablet_checklist
        
        items = ["Item 1", "Item 2", "Item 3"]
        result = tablet_checklist(items, key="check_test")
        
        assert all(not v for v in result.values())

    @patch("streamlit.session_state", {"check_cb_checked": {"A": True, "B": False}})
    @patch("streamlit.button", return_value=False)
    def test_checklist_with_callback(self, mock_btn):
        """Test checklist avec callback."""
        from src.ui.tablet_mode import tablet_checklist
        
        callback = MagicMock()
        items = ["A", "B"]
        
        result = tablet_checklist(items, key="check_cb", on_check=callback)
        
        assert result["A"] is True
        assert result["B"] is False


# ═══════════════════════════════════════════════════════════
# RENDER MODE SELECTOR
# ═══════════════════════════════════════════════════════════


class TestRenderModeSelector:
    """Tests pour render_mode_selector."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.tablet_mode import render_mode_selector
        assert render_mode_selector is not None

    @patch("streamlit.session_state", {})
    @patch("streamlit.sidebar")
    @patch("streamlit.selectbox")
    @patch("streamlit.markdown")
    def test_render_normal_mode(self, mock_md, mock_select, mock_sidebar):
        """Test render en mode normal."""
        from src.ui.tablet_mode import render_mode_selector, TabletMode
        
        mock_sidebar.__enter__ = MagicMock()
        mock_sidebar.__exit__ = MagicMock()
        mock_select.return_value = TabletMode.NORMAL
        
        render_mode_selector()
        
        mock_select.assert_called_once()

    @patch("streamlit.session_state", {"tablet_mode": "kitchen"})
    @patch("streamlit.sidebar")
    @patch("streamlit.selectbox")
    @patch("streamlit.markdown")
    @patch("streamlit.info")
    def test_render_kitchen_mode(self, mock_info, mock_md, mock_select, mock_sidebar):
        """Test render en mode cuisine - affiche info."""
        from src.ui.tablet_mode import render_mode_selector, TabletMode
        
        mock_sidebar.__enter__ = MagicMock()
        mock_sidebar.__exit__ = MagicMock()
        mock_select.return_value = TabletMode.KITCHEN
        
        render_mode_selector()
        
        # Info devrait être affiché en mode cuisine
        mock_info.assert_called_once()


# ═══════════════════════════════════════════════════════════
# INTEGRATION
# ═══════════════════════════════════════════════════════════


class TestTabletModeIntegration:
    """Tests d'intégration."""

    def test_css_constants_exist(self):
        """Test que les constantes CSS existent."""
        from src.ui.tablet_mode import TABLET_CSS
        
        assert TABLET_CSS is not None
        assert len(TABLET_CSS) > 100  # CSS substantiel

    def test_kitchen_css_exists(self):
        """Test que le CSS cuisine existe."""
        from src.ui.tablet_mode import KITCHEN_MODE_CSS
        
        assert KITCHEN_MODE_CSS is not None
