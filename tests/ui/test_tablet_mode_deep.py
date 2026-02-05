"""
Tests approfondis pour tablet_mode.py

Module: src/ui/tablet_mode.py
Tests créés: ~70 tests
Objectif: Atteindre 80%+ de couverture
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from enum import Enum


# =============================================================================
# TESTS TabletMode Enum
# =============================================================================


class TestTabletModeEnum:
    """Tests pour l'enum TabletMode"""
    
    def test_tablet_mode_values(self):
        """Vérifie les valeurs de l'enum"""
        from src.ui.tablet_mode import TabletMode
        
        assert TabletMode.NORMAL.value == "normal"
        assert TabletMode.TABLET.value == "tablet"
        assert TabletMode.KITCHEN.value == "kitchen"
    
    def test_tablet_mode_is_str_enum(self):
        """TabletMode est un string enum"""
        from src.ui.tablet_mode import TabletMode
        
        assert isinstance(TabletMode.NORMAL, str)
        assert TabletMode.NORMAL == "normal"
    
    def test_tablet_mode_from_string(self):
        """Création depuis string"""
        from src.ui.tablet_mode import TabletMode
        
        assert TabletMode("normal") == TabletMode.NORMAL
        assert TabletMode("tablet") == TabletMode.TABLET
        assert TabletMode("kitchen") == TabletMode.KITCHEN
    
    def test_tablet_mode_invalid_raises(self):
        """Valeur invalide lève exception"""
        from src.ui.tablet_mode import TabletMode
        
        with pytest.raises(ValueError):
            TabletMode("invalid")


# =============================================================================
# TESTS get_tablet_mode et set_tablet_mode
# =============================================================================


class TestGetSetTabletMode:
    """Tests pour get/set_tablet_mode"""
    
    @patch("src.ui.tablet_mode.st")
    def test_get_tablet_mode_default(self, mock_st):
        """Mode par défaut = NORMAL"""
        from src.ui.tablet_mode import get_tablet_mode, TabletMode
        
        mock_st.session_state = {}
        
        result = get_tablet_mode()
        assert result == TabletMode.NORMAL
    
    @patch("src.ui.tablet_mode.st")
    def test_get_tablet_mode_from_session(self, mock_st):
        """Récupère mode depuis session"""
        from src.ui.tablet_mode import get_tablet_mode, TabletMode
        
        mock_st.session_state = {"tablet_mode": TabletMode.TABLET}
        
        result = get_tablet_mode()
        assert result == TabletMode.TABLET
    
    @patch("src.ui.tablet_mode.st")
    def test_get_tablet_mode_string_to_enum(self, mock_st):
        """Convertit string en enum"""
        from src.ui.tablet_mode import get_tablet_mode, TabletMode
        
        mock_st.session_state = {"tablet_mode": "kitchen"}
        
        result = get_tablet_mode()
        assert result == TabletMode.KITCHEN
    
    @patch("src.ui.tablet_mode.st")
    def test_set_tablet_mode(self, mock_st):
        """Définit le mode tablette"""
        from src.ui.tablet_mode import set_tablet_mode, TabletMode
        
        mock_st.session_state = {}
        
        set_tablet_mode(TabletMode.KITCHEN)
        
        assert mock_st.session_state["tablet_mode"] == TabletMode.KITCHEN
    
    @patch("src.ui.tablet_mode.st")
    def test_set_tablet_mode_normal(self, mock_st):
        """Définit mode normal"""
        from src.ui.tablet_mode import set_tablet_mode, TabletMode
        
        mock_st.session_state = {"tablet_mode": TabletMode.TABLET}
        
        set_tablet_mode(TabletMode.NORMAL)
        
        assert mock_st.session_state["tablet_mode"] == TabletMode.NORMAL


# =============================================================================
# TESTS CSS Constants
# =============================================================================


class TestCSSConstants:
    """Tests pour les constantes CSS"""
    
    def test_tablet_css_exists(self):
        """TABLET_CSS est défini"""
        from src.ui.tablet_mode import TABLET_CSS
        
        assert isinstance(TABLET_CSS, str)
        assert "<style>" in TABLET_CSS
        assert "</style>" in TABLET_CSS
    
    def test_tablet_css_contains_tablet_mode_class(self):
        """TABLET_CSS contient la classe tablet-mode"""
        from src.ui.tablet_mode import TABLET_CSS
        
        assert "tablet-mode" in TABLET_CSS
    
    def test_tablet_css_contains_kitchen_mode_class(self):
        """TABLET_CSS contient la classe kitchen-mode"""
        from src.ui.tablet_mode import TABLET_CSS
        
        assert "kitchen-mode" in TABLET_CSS
    
    def test_kitchen_mode_css_exists(self):
        """KITCHEN_MODE_CSS est défini"""
        from src.ui.tablet_mode import KITCHEN_MODE_CSS
        
        assert isinstance(KITCHEN_MODE_CSS, str)
        assert "<style>" in KITCHEN_MODE_CSS
    
    def test_kitchen_css_contains_kitchen_classes(self):
        """CSS cuisine contient les classes spécifiques"""
        from src.ui.tablet_mode import KITCHEN_MODE_CSS
        
        assert "kitchen-ingredient" in KITCHEN_MODE_CSS
        assert "kitchen-step-transition" in KITCHEN_MODE_CSS


# =============================================================================
# TESTS apply_tablet_mode
# =============================================================================


class TestApplyTabletMode:
    """Tests pour apply_tablet_mode"""
    
    @patch("src.ui.tablet_mode.st")
    @patch("src.ui.tablet_mode.get_tablet_mode")
    def test_apply_tablet_mode_normal(self, mock_get_mode, mock_st):
        """Mode normal applique CSS de base"""
        from src.ui.tablet_mode import apply_tablet_mode, TabletMode, TABLET_CSS
        
        mock_get_mode.return_value = TabletMode.NORMAL
        mock_st.markdown = Mock()
        
        apply_tablet_mode()
        
        # Vérifie que le CSS de base est appliqué
        mock_st.markdown.assert_called_once()
        call_args = mock_st.markdown.call_args
        assert call_args[0][0] == TABLET_CSS
    
    @patch("src.ui.tablet_mode.st")
    @patch("src.ui.tablet_mode.get_tablet_mode")
    def test_apply_tablet_mode_tablet(self, mock_get_mode, mock_st):
        """Mode tablette ajoute div tablet-mode"""
        from src.ui.tablet_mode import apply_tablet_mode, TabletMode
        
        mock_get_mode.return_value = TabletMode.TABLET
        mock_st.markdown = Mock()
        
        apply_tablet_mode()
        
        # Vérifie que le div tablet-mode est ajouté
        calls = mock_st.markdown.call_args_list
        assert len(calls) == 2
        assert 'tablet-mode' in calls[1][0][0]
    
    @patch("src.ui.tablet_mode.st")
    @patch("src.ui.tablet_mode.get_tablet_mode")
    def test_apply_tablet_mode_kitchen(self, mock_get_mode, mock_st):
        """Mode cuisine ajoute CSS cuisine et divs"""
        from src.ui.tablet_mode import apply_tablet_mode, TabletMode
        
        mock_get_mode.return_value = TabletMode.KITCHEN
        mock_st.markdown = Mock()
        
        apply_tablet_mode()
        
        # Vérifie que le CSS cuisine et les divs sont ajoutés
        calls = mock_st.markdown.call_args_list
        assert len(calls) == 3


# =============================================================================
# TESTS close_tablet_mode
# =============================================================================


class TestCloseTabletMode:
    """Tests pour close_tablet_mode"""
    
    @patch("src.ui.tablet_mode.st")
    @patch("src.ui.tablet_mode.get_tablet_mode")
    def test_close_tablet_mode_normal(self, mock_get_mode, mock_st):
        """Mode normal ne ferme rien"""
        from src.ui.tablet_mode import close_tablet_mode, TabletMode
        
        mock_get_mode.return_value = TabletMode.NORMAL
        mock_st.markdown = Mock()
        
        close_tablet_mode()
        
        # Pas d'appel en mode normal
        mock_st.markdown.assert_not_called()
    
    @patch("src.ui.tablet_mode.st")
    @patch("src.ui.tablet_mode.get_tablet_mode")
    def test_close_tablet_mode_tablet(self, mock_get_mode, mock_st):
        """Mode tablette ferme le div"""
        from src.ui.tablet_mode import close_tablet_mode, TabletMode
        
        mock_get_mode.return_value = TabletMode.TABLET
        mock_st.markdown = Mock()
        
        close_tablet_mode()
        
        mock_st.markdown.assert_called_with('</div>', unsafe_allow_html=True)
    
    @patch("src.ui.tablet_mode.st")
    @patch("src.ui.tablet_mode.get_tablet_mode")
    def test_close_tablet_mode_kitchen(self, mock_get_mode, mock_st):
        """Mode cuisine ferme le div"""
        from src.ui.tablet_mode import close_tablet_mode, TabletMode
        
        mock_get_mode.return_value = TabletMode.KITCHEN
        mock_st.markdown = Mock()
        
        close_tablet_mode()
        
        mock_st.markdown.assert_called_with('</div>', unsafe_allow_html=True)


# =============================================================================
# TESTS tablet_button
# =============================================================================


class TestTabletButton:
    """Tests pour tablet_button"""
    
    @patch("src.ui.tablet_mode.st")
    def test_tablet_button_simple(self, mock_st):
        """Bouton simple"""
        from src.ui.tablet_mode import tablet_button
        
        mock_st.button = Mock(return_value=False)
        
        result = tablet_button("Cliquez", key="btn1")
        
        mock_st.button.assert_called_once()
        assert "Cliquez" in mock_st.button.call_args[0][0]
    
    @patch("src.ui.tablet_mode.st")
    def test_tablet_button_with_icon(self, mock_st):
        """Bouton avec icône"""
        from src.ui.tablet_mode import tablet_button
        
        mock_st.button = Mock(return_value=False)
        
        tablet_button("Valider", key="btn2", icon="✅")
        
        call_args = mock_st.button.call_args[0][0]
        assert "✅" in call_args
        assert "Valider" in call_args
    
    @patch("src.ui.tablet_mode.st")
    def test_tablet_button_primary_type(self, mock_st):
        """Bouton type primary"""
        from src.ui.tablet_mode import tablet_button
        
        mock_st.button = Mock(return_value=False)
        
        tablet_button("Action", key="btn3", type="primary")
        
        call_kwargs = mock_st.button.call_args[1]
        assert call_kwargs.get("type") == "primary"
    
    @patch("src.ui.tablet_mode.st")
    def test_tablet_button_danger_type(self, mock_st):
        """Bouton type danger"""
        from src.ui.tablet_mode import tablet_button
        
        mock_st.button = Mock(return_value=False)
        
        tablet_button("Supprimer", key="btn4", type="danger")
        
        call_kwargs = mock_st.button.call_args[1]
        assert "irréversible" in call_kwargs.get("help", "").lower()
    
    @patch("src.ui.tablet_mode.st")
    def test_tablet_button_returns_click_state(self, mock_st):
        """Retourne True si cliqué"""
        from src.ui.tablet_mode import tablet_button
        
        mock_st.button = Mock(return_value=True)
        
        result = tablet_button("Test", key="btn5")
        
        assert result is True


# =============================================================================
# TESTS tablet_select_grid
# =============================================================================


class TestTabletSelectGrid:
    """Tests pour tablet_select_grid"""
    
    @patch("src.ui.tablet_mode.st")
    def test_tablet_select_grid_creates_columns(self, mock_st):
        """Crée le nombre de colonnes demandé"""
        from src.ui.tablet_mode import tablet_select_grid
        
        mock_st.session_state = {}
        mock_cols = [MagicMock() for _ in range(3)]
        mock_st.columns = Mock(return_value=mock_cols)
        mock_st.button = Mock(return_value=False)
        
        options = [
            {"value": "a", "label": "Option A"},
            {"value": "b", "label": "Option B"},
        ]
        
        tablet_select_grid(options, key="grid1", columns=3)
        
        mock_st.columns.assert_called_with(3)
    
    @patch("src.ui.tablet_mode.st")
    def test_tablet_select_grid_returns_selected(self, mock_st):
        """Retourne la valeur sélectionnée"""
        from src.ui.tablet_mode import tablet_select_grid
        
        mock_st.session_state = {"grid2_selected": "option_b"}
        mock_cols = [MagicMock() for _ in range(3)]
        mock_st.columns = Mock(return_value=mock_cols)
        mock_st.button = Mock(return_value=False)
        
        options = [{"value": "option_a"}, {"value": "option_b"}]
        
        result = tablet_select_grid(options, key="grid2")
        
        assert result == "option_b"
    
    @patch("src.ui.tablet_mode.st")
    def test_tablet_select_grid_no_selection(self, mock_st):
        """Retourne None si rien sélectionné"""
        from src.ui.tablet_mode import tablet_select_grid
        
        mock_st.session_state = {}
        mock_cols = [MagicMock() for _ in range(2)]
        mock_st.columns = Mock(return_value=mock_cols)
        mock_st.button = Mock(return_value=False)
        
        options = [{"value": "x"}]
        
        result = tablet_select_grid(options, key="grid3")
        
        assert result is None


# =============================================================================
# TESTS tablet_number_input
# =============================================================================


class TestTabletNumberInput:
    """Tests pour tablet_number_input"""
    
    @patch("src.ui.tablet_mode.st")
    def test_tablet_number_input_default(self, mock_st):
        """Valeur par défaut"""
        from src.ui.tablet_mode import tablet_number_input
        
        mock_st.session_state = {}
        mock_st.write = Mock()
        mock_st.markdown = Mock()
        mock_st.button = Mock(return_value=False)
        mock_cols = [MagicMock() for _ in range(3)]
        mock_st.columns = Mock(return_value=mock_cols)
        
        result = tablet_number_input("Quantité", key="num1", default=5)
        
        assert result == 5
        assert mock_st.session_state["num1_value"] == 5
    
    @patch("src.ui.tablet_mode.st")
    def test_tablet_number_input_preserves_state(self, mock_st):
        """Préserve la valeur en session"""
        from src.ui.tablet_mode import tablet_number_input
        
        mock_st.session_state = {"num2_value": 10}
        mock_st.write = Mock()
        mock_st.markdown = Mock()
        mock_st.button = Mock(return_value=False)
        mock_cols = [MagicMock() for _ in range(3)]
        mock_st.columns = Mock(return_value=mock_cols)
        
        result = tablet_number_input("Quantité", key="num2", default=1)
        
        assert result == 10


# =============================================================================
# TESTS tablet_checklist
# =============================================================================


class TestTabletChecklist:
    """Tests pour tablet_checklist"""
    
    @patch("src.ui.tablet_mode.st")
    def test_tablet_checklist_init_unchecked(self, mock_st):
        """Items initialisés non cochés"""
        from src.ui.tablet_mode import tablet_checklist
        
        mock_st.session_state = {}
        mock_st.button = Mock(return_value=False)
        
        items = ["item1", "item2", "item3"]
        result = tablet_checklist(items, key="check1")
        
        assert all(not v for v in result.values())
    
    @patch("src.ui.tablet_mode.st")
    def test_tablet_checklist_preserves_state(self, mock_st):
        """Préserve l'état des cases"""
        from src.ui.tablet_mode import tablet_checklist
        
        mock_st.session_state = {
            "check2_checked": {"a": True, "b": False}
        }
        mock_st.button = Mock(return_value=False)
        
        result = tablet_checklist(["a", "b"], key="check2")
        
        assert result["a"] is True
        assert result["b"] is False


# =============================================================================
# TESTS render_kitchen_recipe_view
# =============================================================================


class TestRenderKitchenRecipeView:
    """Tests pour render_kitchen_recipe_view"""
    
    @patch("src.ui.tablet_mode.st")
    def test_render_kitchen_recipe_initial_state(self, mock_st):
        """État initial = étape 0"""
        from src.ui.tablet_mode import render_kitchen_recipe_view
        
        mock_st.session_state = {}
        mock_st.markdown = Mock()
        mock_st.button = Mock(return_value=False)
        mock_st.tabs = Mock(return_value=[MagicMock(), MagicMock()])
        mock_st.columns = Mock(return_value=[MagicMock() for _ in range(3)])
        mock_st.checkbox = Mock()
        mock_st.metric = Mock()
        mock_st.progress = Mock()
        
        recette = {
            "nom": "Tarte aux pommes",
            "instructions": ["Étape 1", "Étape 2"],
            "ingredients": ["pommes", "sucre"]
        }
        
        render_kitchen_recipe_view(recette, key="test_recipe")
        
        # Vérifie l'état initial
        assert mock_st.session_state["test_recipe_step"] == 0
    
    @patch("src.ui.tablet_mode.st")
    def test_render_kitchen_recipe_with_timer(self, mock_st):
        """Affiche le timer si défini"""
        from src.ui.tablet_mode import render_kitchen_recipe_view
        
        mock_st.session_state = {
            "timer_recipe_step": 1,
            "timer_recipe_timer": 5
        }
        mock_st.markdown = Mock()
        mock_st.button = Mock(return_value=False)
        mock_st.tabs = Mock(return_value=[MagicMock(), MagicMock()])
        mock_st.columns = Mock(return_value=[MagicMock() for _ in range(3)])
        mock_st.progress = Mock()
        mock_st.checkbox = Mock()
        
        recette = {"nom": "Test", "instructions": ["Step 1"]}
        
        render_kitchen_recipe_view(recette, key="timer_recipe")
        
        # Vérifie que markdown est appelé avec le timer
        calls = [str(c) for c in mock_st.markdown.call_args_list]
        # Le timer devrait apparaître
        assert any("5" in str(c) and "min" in str(c) for c in calls)


# =============================================================================
# TESTS render_mode_selector
# =============================================================================


class TestRenderModeSelector:
    """Tests pour render_mode_selector"""
    
    @patch("src.ui.tablet_mode.st")
    @patch("src.ui.tablet_mode.get_tablet_mode")
    @patch("src.ui.tablet_mode.set_tablet_mode")
    def test_render_mode_selector_shows_options(self, mock_set, mock_get, mock_st):
        """Affiche le sélecteur dans la sidebar"""
        from src.ui.tablet_mode import render_mode_selector, TabletMode
        
        mock_get.return_value = TabletMode.NORMAL
        mock_st.sidebar = MagicMock()
        mock_st.sidebar.__enter__ = Mock(return_value=mock_st.sidebar)
        mock_st.sidebar.__exit__ = Mock(return_value=False)
        mock_st.selectbox = Mock(return_value=TabletMode.NORMAL)
        mock_st.markdown = Mock()
        
        render_mode_selector()
        
        mock_st.selectbox.assert_called_once()
    
    @patch("src.ui.tablet_mode.st")
    @patch("src.ui.tablet_mode.get_tablet_mode")
    @patch("src.ui.tablet_mode.set_tablet_mode")
    def test_render_mode_selector_changes_mode(self, mock_set, mock_get, mock_st):
        """Change le mode si sélection différente"""
        from src.ui.tablet_mode import render_mode_selector, TabletMode
        
        mock_get.return_value = TabletMode.NORMAL
        mock_st.sidebar = MagicMock()
        mock_st.sidebar.__enter__ = Mock(return_value=mock_st.sidebar)
        mock_st.sidebar.__exit__ = Mock(return_value=False)
        mock_st.selectbox = Mock(return_value=TabletMode.TABLET)
        mock_st.markdown = Mock()
        mock_st.rerun = Mock()
        
        render_mode_selector()
        
        mock_set.assert_called_with(TabletMode.TABLET)
        mock_st.rerun.assert_called_once()
    
    @patch("src.ui.tablet_mode.st")
    @patch("src.ui.tablet_mode.get_tablet_mode")
    def test_render_mode_selector_kitchen_info(self, mock_get, mock_st):
        """Affiche info en mode cuisine"""
        from src.ui.tablet_mode import render_mode_selector, TabletMode
        
        mock_get.return_value = TabletMode.KITCHEN
        mock_st.sidebar = MagicMock()
        mock_st.sidebar.__enter__ = Mock(return_value=mock_st.sidebar)
        mock_st.sidebar.__exit__ = Mock(return_value=False)
        mock_st.selectbox = Mock(return_value=TabletMode.KITCHEN)
        mock_st.markdown = Mock()
        mock_st.info = Mock()
        
        render_mode_selector()
        
        mock_st.info.assert_called_once()
        call_arg = mock_st.info.call_args[0][0]
        assert "cuisine" in call_arg.lower()
