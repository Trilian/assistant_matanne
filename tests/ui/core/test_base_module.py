"""
Tests complets pour src/ui/core/base_module.py
Couverture cible: >80%
"""

import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass, field


# ═══════════════════════════════════════════════════════════
# CONFIGURATION MODULE
# ═══════════════════════════════════════════════════════════


class TestConfigurationModule:
    """Tests pour ConfigurationModule."""

    def test_configuration_module_import(self):
        """Test import réussi."""
        from src.ui.core.base_module import ConfigurationModule
        assert ConfigurationModule is not None

    def test_configuration_module_creation(self):
        """Test création basique."""
        from src.ui.core.base_module import ConfigurationModule
        
        config = ConfigurationModule(
            name="test",
            title="Test Module",
            icon="🧪",
            service=MagicMock()
        )
        
        assert config.name == "test"
        assert config.title == "Test Module"
        assert config.icon == "🧪"

    def test_configuration_module_defaults(self):
        """Test valeurs par défaut."""
        from src.ui.core.base_module import ConfigurationModule
        
        config = ConfigurationModule(
            name="test",
            title="Test",
            icon="🧪",
            service=MagicMock()
        )
        
        assert config.display_fields == []
        assert config.search_fields == []
        assert config.filters_config == {}
        assert config.items_per_page == 20
        assert config.export_formats == ["csv", "json"]

    def test_configuration_module_with_stats(self):
        """Test avec stats config."""
        from src.ui.core.base_module import ConfigurationModule
        
        stats = [{"label": "Total", "value_key": "total"}]
        
        config = ConfigurationModule(
            name="test",
            title="Test",
            icon="🧪",
            service=MagicMock(),
            stats_config=stats
        )
        
        assert config.stats_config == stats

    def test_alias_module_config(self):
        """Test alias ModuleConfig."""
        from src.ui.core.base_module import ModuleConfig, ConfigurationModule
        assert ModuleConfig is ConfigurationModule


# ═══════════════════════════════════════════════════════════
# MODULE UI BASE
# ═══════════════════════════════════════════════════════════


class TestModuleUIBase:
    """Tests pour ModuleUIBase."""

    def test_module_ui_base_import(self):
        """Test import réussi."""
        from src.ui.core.base_module import ModuleUIBase
        assert ModuleUIBase is not None

    @patch("streamlit.session_state", {})
    def test_module_ui_base_creation(self):
        """Test création."""
        from src.ui.core.base_module import ModuleUIBase, ConfigurationModule
        
        config = ConfigurationModule(
            name="test",
            title="Test",
            icon="🧪",
            service=MagicMock()
        )
        
        module = ModuleUIBase(config)
        
        assert module.config == config
        assert module.session_key == "module_test"

    @patch("streamlit.session_state", {})
    def test_module_ui_base_init_session(self):
        """Test initialisation session state."""
        from src.ui.core.base_module import ModuleUIBase, ConfigurationModule
        import streamlit as st
        
        config = ConfigurationModule(
            name="init_test",
            title="Test",
            icon="🧪",
            service=MagicMock()
        )
        
        module = ModuleUIBase(config)
        
        assert "module_init_test" in st.session_state
        assert st.session_state["module_init_test"]["current_page"] == 1
        assert st.session_state["module_init_test"]["view_mode"] == "grid"

    def test_alias_base_module_ui(self):
        """Test alias BaseModuleUI."""
        from src.ui.core.base_module import BaseModuleUI, ModuleUIBase
        assert BaseModuleUI is ModuleUIBase


# ═══════════════════════════════════════════════════════════
# RENDER METHODS
# ═══════════════════════════════════════════════════════════


class TestModuleUIBaseRender:
    """Tests pour les méthodes render."""

    @patch("streamlit.session_state", {})
    @patch("streamlit.title")
    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=False)
    def test_render_header(self, mock_btn, mock_cols, mock_title):
        """Test _render_header."""
        from src.ui.core.base_module import ModuleUIBase, ConfigurationModule
        
        mock_cols.return_value = [MagicMock(), MagicMock()]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()
        
        config = ConfigurationModule(
            name="header_test",
            title="Header Test",
            icon="🧪",
            service=MagicMock()
        )
        
        module = ModuleUIBase(config)
        module._render_header()
        
        mock_cols.assert_called_once()

    @patch("streamlit.session_state", {"module_view_test": {"view_mode": "grid", "current_page": 1, "search_term": "", "filters": {}, "selected_items": []}})
    @patch("streamlit.title")
    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=True)
    @patch("streamlit.rerun")
    def test_render_header_toggle_view(self, mock_rerun, mock_btn, mock_cols, mock_title):
        """Test toggle view mode."""
        from src.ui.core.base_module import ModuleUIBase, ConfigurationModule
        import streamlit as st
        
        mock_cols.return_value = [MagicMock(), MagicMock()]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()
        
        config = ConfigurationModule(
            name="view_test",
            title="View Test",
            icon="🧪",
            service=MagicMock()
        )
        
        module = ModuleUIBase(config)
        
        try:
            module._render_header()
        except Exception:
            pass
        
        # Le view mode aurait dû changer
        assert st.session_state["module_view_test"]["view_mode"] == "list"

    @patch("streamlit.session_state", {})
    def test_render_search_filters(self):
        """Test _render_search_filters."""
        from src.ui.core.base_module import ModuleUIBase, ConfigurationModule
        
        config = ConfigurationModule(
            name="search_test",
            title="Search Test",
            icon="🧪",
            service=MagicMock(),
            search_fields=["nom"]
        )
        
        with patch("src.ui.core.base_module.barre_recherche", return_value=""):
            module = ModuleUIBase(config)
            module._render_search_filters()

    @patch("streamlit.session_state", {})
    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.download_button", return_value=False)
    def test_render_actions(self, mock_dl, mock_btn, mock_cols):
        """Test _render_actions."""
        from src.ui.core.base_module import ModuleUIBase, ConfigurationModule
        
        # Le code utilise col1, col2, col3 = st.columns(3)
        mock_cols.return_value = [MagicMock(), MagicMock(), MagicMock()]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()
        
        config = ConfigurationModule(
            name="action_test",
            title="Action Test",
            icon="🧪",
            service=MagicMock()
        )
        
        module = ModuleUIBase(config)
        module._render_actions()

    @patch("streamlit.session_state", {})
    @patch("streamlit.columns")
    def test_render_grid(self, mock_cols):
        """Test _render_grid."""
        from src.ui.core.base_module import ModuleUIBase, ConfigurationModule
        
        mock_cols.return_value = [MagicMock() for _ in range(3)]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()
        
        config = ConfigurationModule(
            name="grid_test",
            title="Grid Test",
            icon="🧪",
            service=MagicMock(),
            display_fields=[{"key": "nom"}]
        )
        
        module = ModuleUIBase(config)
        
        with patch.object(module, "_render_carte_item"):
            items = [{"id": 1, "nom": "Item1"}, {"id": 2, "nom": "Item2"}]
            module._render_grid(items)

    @patch("streamlit.session_state", {})
    @patch("streamlit.expander")
    def test_render_list(self, mock_expander):
        """Test _render_list."""
        from src.ui.core.base_module import ModuleUIBase, ConfigurationModule
        
        mock_expander.return_value.__enter__ = MagicMock()
        mock_expander.return_value.__exit__ = MagicMock()
        
        config = ConfigurationModule(
            name="list_test",
            title="List Test",
            icon="🧪",
            service=MagicMock(),
            display_fields=[{"key": "nom"}]
        )
        
        module = ModuleUIBase(config)
        
        items = [{"id": 1, "nom": "Item1"}]
        module._render_list(items)

    @patch("streamlit.session_state", {})
    def test_item_to_dict_with_dict(self):
        """Test _item_to_dict avec dict."""
        from src.ui.core.base_module import ModuleUIBase, ConfigurationModule
        
        config = ConfigurationModule(
            name="dict_test",
            title="Dict Test",
            icon="🧪",
            service=MagicMock()
        )
        
        module = ModuleUIBase(config)
        
        item = {"id": 1, "nom": "Test"}
        result = module._item_to_dict(item)
        
        assert result == item


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


class TestFactory:
    """Tests pour les factories."""

    @patch("streamlit.session_state", {})
    def test_creer_module_ui(self):
        """Test creer_module_ui."""
        from src.ui.core.base_module import creer_module_ui, ConfigurationModule, ModuleUIBase
        
        config = ConfigurationModule(
            name="factory_test",
            title="Factory Test",
            icon="🧪",
            service=MagicMock()
        )
        
        module = creer_module_ui(config)
        
        assert isinstance(module, ModuleUIBase)

    @patch("streamlit.session_state", {})
    def test_create_module_ui_alias(self):
        """Test alias create_module_ui."""
        from src.ui.core.base_module import create_module_ui, creer_module_ui
        assert create_module_ui is creer_module_ui


# ═══════════════════════════════════════════════════════════
# INTEGRATION
# ═══════════════════════════════════════════════════════════


class TestBaseModuleIntegration:
    """Tests d'intégration."""

    def test_exports_from_core(self):
        """Test exports depuis core."""
        from src.ui.core import (
            ConfigurationModule,
            ModuleUIBase,
            creer_module_ui,
            ModuleConfig,
            BaseModuleUI,
            create_module_ui,
        )
        
        assert ConfigurationModule is not None
        assert ModuleUIBase is not None
        assert creer_module_ui is not None

    def test_exports_from_ui(self):
        """Test exports depuis ui."""
        from src.ui import (
            ConfigurationModule,
            ModuleUIBase,
            creer_module_ui,
        )
        
        assert ConfigurationModule is not None
        assert ModuleUIBase is not None
        assert creer_module_ui is not None
