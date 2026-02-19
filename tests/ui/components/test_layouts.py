"""
Tests complets pour src/ui/components/layouts.py
Couverture cible: >80%

Note: Tests pour section_pliable, disposition_onglets, conteneur_carte supprimés
      (composants retirés lors du nettoyage UI)
"""

from unittest.mock import MagicMock, patch

# ═══════════════════════════════════════════════════════════
# DISPOSITION_GRILLE (grid_layout)
# ═══════════════════════════════════════════════════════════


class TestDispositionGrille:
    """Tests pour disposition_grille()."""

    def test_disposition_grille_import(self):
        """Test import réussi."""
        from src.ui.components.layouts import disposition_grille

        assert callable(disposition_grille)

    @patch("streamlit.info")
    def test_disposition_grille_empty(self, mock_info):
        """Test avec liste vide."""
        from src.ui.components.layouts import disposition_grille

        disposition_grille([], colonnes_par_ligne=3)

        mock_info.assert_called_once_with("Aucun élément")

    @patch("streamlit.columns")
    @patch("streamlit.write")
    def test_disposition_grille_basic(self, mock_write, mock_cols):
        """Test grille de base."""
        from src.ui.components.layouts import disposition_grille

        mock_cols.return_value = [MagicMock(), MagicMock(), MagicMock()]

        items = [{"id": 1}, {"id": 2}]

        disposition_grille(items, colonnes_par_ligne=3)

        mock_cols.assert_called()

    @patch("streamlit.columns")
    def test_disposition_grille_custom_renderer(self, mock_cols):
        """Test avec rendu personnalisé."""
        from src.ui.components.layouts import disposition_grille

        mock_cols.return_value = [MagicMock(), MagicMock()]
        renderer = MagicMock()

        items = [{"id": 1}, {"id": 2}]

        disposition_grille(items, colonnes_par_ligne=2, rendu_carte=renderer, cle="test")

        assert renderer.call_count >= 1


# ═══════════════════════════════════════════════════════════
# CARTE_ITEM (item_card)
# ═══════════════════════════════════════════════════════════


class TestCarteItem:
    """Tests pour carte_item()."""

    def test_carte_item_import(self):
        """Test import réussi."""
        from src.ui.components.layouts import carte_item

        assert callable(carte_item)

    @patch("streamlit.container")
    @patch("streamlit.markdown")
    def test_carte_item_basic(self, mock_markdown, mock_container):
        """Test carte basique."""
        from src.ui.components.layouts import carte_item

        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()

        carte_item(titre="Test", metadonnees=["info1", "info2"])

        mock_markdown.assert_called()

    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.caption")
    @patch("streamlit.columns")
    def test_carte_item_with_status(self, mock_cols, mock_caption, mock_markdown, mock_container):
        """Test carte avec statut."""
        from src.ui.components.layouts import carte_item

        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        mock_cols.return_value = [MagicMock(), MagicMock()]

        carte_item(titre="Test", metadonnees=["info"], statut="actif", couleur_statut="#4CAF50")

        assert mock_markdown.called

    @patch("streamlit.container")
    @patch("streamlit.markdown")
    @patch("streamlit.image")
    @patch("streamlit.columns")
    def test_carte_item_with_image(self, mock_cols, mock_image, mock_markdown, mock_container):
        """Test carte avec image."""
        from src.ui.components.layouts import carte_item

        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        mock_cols.return_value = [MagicMock(), MagicMock()]

        carte_item(titre="Test", metadonnees=[], url_image="http://example.com/img.jpg")

        # Image devrait être appelée
        assert mock_cols.called


# ═══════════════════════════════════════════════════════════
# TESTS D'INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestLayoutsIntegration:
    """Tests d'intégration pour le module layouts."""

    def test_functions_exported(self):
        """Test que les fonctions conservées sont exportées."""
        from src.ui.components import layouts

        assert hasattr(layouts, "disposition_grille")
        assert hasattr(layouts, "carte_item")

    def test_imports_from_components(self):
        """Test imports depuis components."""
        from src.ui.components import (
            carte_item,
            disposition_grille,
        )

        assert disposition_grille is not None
        assert carte_item is not None

    def test_imports_from_ui(self):
        """Test imports depuis ui."""
        from src.ui import (
            carte_item,
            disposition_grille,
        )

        assert disposition_grille is not None
        assert carte_item is not None
