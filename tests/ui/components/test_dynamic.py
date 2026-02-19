"""
Tests complets pour src/ui/components/dynamic.py
Couverture cible: >80%

Note: Tests pour ListeDynamique et AssistantEtapes supprimés
      (composants retirés lors du nettoyage UI)
"""

from unittest.mock import patch

# ═══════════════════════════════════════════════════════════
# MODALE (Modal)
# ═══════════════════════════════════════════════════════════


class TestModale:
    """Tests pour la classe Modale."""

    def test_modale_import(self):
        """Test import réussi."""
        from src.ui.components.dynamic import Modale

        assert Modale is not None

    @patch("streamlit.session_state", {})
    def test_modale_creation(self):
        """Test création de Modale."""
        from src.ui.components.dynamic import Modale

        modal = Modale("test")

        assert modal.key == "modal_test"

    @patch("streamlit.session_state", {})
    def test_modale_show(self):
        """Test affichage modal."""
        import streamlit as st

        from src.ui.components.dynamic import Modale

        modal = Modale("show_test")
        modal.show()

        assert st.session_state.get("modal_show_test") is True

    @patch("streamlit.session_state", {"modal_close_test": True})
    @patch("streamlit.rerun")
    def test_modale_close(self, mock_rerun):
        """Test fermeture modal."""
        import streamlit as st

        from src.ui.components.dynamic import Modale

        modal = Modale("close_test")

        try:
            modal.close()
        except Exception:
            pass  # rerun arrête l'exécution

        assert st.session_state.get("modal_close_test") is False

    @patch("streamlit.session_state", {"modal_is_test": True})
    def test_modale_is_showing_true(self):
        """Test is_showing retourne True."""
        from src.ui.components.dynamic import Modale

        modal = Modale("is_test")

        assert modal.is_showing() is True

    @patch("streamlit.session_state", {"modal_not_test": False})
    def test_modale_is_showing_false(self):
        """Test is_showing retourne False."""
        from src.ui.components.dynamic import Modale

        modal = Modale("not_test")

        assert modal.is_showing() is False

    @patch("streamlit.session_state", {})
    @patch("streamlit.button")
    def test_modale_confirm(self, mock_btn):
        """Test bouton confirmer."""
        from src.ui.components.dynamic import Modale

        mock_btn.return_value = True

        modal = Modale("confirm_test")
        result = modal.confirm()

        mock_btn.assert_called_once()
        assert result is True

    @patch("streamlit.session_state", {})
    @patch("streamlit.button", return_value=False)
    def test_modale_cancel_no_click(self, mock_btn):
        """Test bouton annuler sans clic."""
        from src.ui.components.dynamic import Modale

        modal = Modale("cancel_test")
        modal.cancel()

        mock_btn.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS D'INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestDynamicIntegration:
    """Tests d'intégration pour le module dynamic."""

    def test_modale_exported(self):
        """Test que Modale est exportée."""
        from src.ui.components import dynamic

        assert hasattr(dynamic, "Modale")

    def test_import_modale_from_components(self):
        """Test import depuis components."""
        from src.ui.components import Modale

        assert Modale is not None

    def test_import_modale_from_ui(self):
        """Test import depuis ui."""
        from src.ui import Modale

        assert Modale is not None


# ═══════════════════════════════════════════════════════════
# TESTS DE RENDER (couverture lignes manquantes)
# ═══════════════════════════════════════════════════════════


class TestModaleRender:
    """Tests pour les méthodes render de Modale."""

    @patch("streamlit.session_state", {"modal_cancel_click": False})
    @patch("streamlit.button", return_value=True)
    @patch("streamlit.rerun")
    def test_modale_cancel_with_click(self, mock_rerun, mock_btn):
        """Test bouton annuler avec clic - ligne 51."""
        from src.ui.components.dynamic import Modale

        modal = Modale("cancel_click")

        try:
            modal.cancel()
        except Exception:
            pass

        mock_btn.assert_called_once()
