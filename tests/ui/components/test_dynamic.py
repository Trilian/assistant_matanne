"""
Tests complets pour src/ui/components/dynamic.py
Couverture cible: >80%

Note: La classe Modale a été remplacée par confirm_dialog (basé sur @st.dialog).
      Ces tests couvrent la nouvelle API.
"""

from unittest.mock import MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════
# CONFIRM_DIALOG
# ═══════════════════════════════════════════════════════════


class TestConfirmDialog:
    """Tests pour la fonction confirm_dialog."""

    def test_confirm_dialog_import(self):
        """Test import réussi."""
        from src.ui.components.dynamic import confirm_dialog

        assert confirm_dialog is not None
        assert callable(confirm_dialog)

    def test_confirm_dialog_exported_in_all(self):
        """Test que confirm_dialog est dans __all__."""
        from src.ui.components import dynamic

        assert "confirm_dialog" in dynamic.__all__


# ═══════════════════════════════════════════════════════════
# TESTS D'INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestDynamicIntegration:
    """Tests d'intégration pour le module dynamic."""

    def test_confirm_dialog_exported(self):
        """Test que confirm_dialog est exportée."""
        from src.ui.components import dynamic

        assert hasattr(dynamic, "confirm_dialog")

    def test_import_confirm_dialog_from_components(self):
        """Test import depuis components."""
        from src.ui.components import confirm_dialog

        assert confirm_dialog is not None

    def test_module_all_list(self):
        """Test que __all__ contient les exports attendus."""
        from src.ui.components import dynamic

        assert isinstance(dynamic.__all__, list)
        assert "confirm_dialog" in dynamic.__all__
