"""
Tests pour src/ui/layout/sidebar.py (stubs deprecated).
"""

import warnings

import pytest


class TestSidebarDeprecated:
    """Vérifie que les stubs deprecated fonctionnent."""

    def test_import_modules_menu(self):
        """MODULES_MENU est un dict vide (deprecated)."""
        from src.ui.layout.sidebar import MODULES_MENU

        assert isinstance(MODULES_MENU, dict)
        assert len(MODULES_MENU) == 0

    def test_afficher_sidebar_warns(self):
        """afficher_sidebar() émet un DeprecationWarning."""
        from src.ui.layout.sidebar import afficher_sidebar

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            afficher_sidebar()
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()

    def test_layout_init_exports(self):
        """Les exports rétrocompatibles sont disponibles."""
        from src.ui.layout import MODULES_MENU, afficher_sidebar

        assert MODULES_MENU is not None
        assert callable(afficher_sidebar)
