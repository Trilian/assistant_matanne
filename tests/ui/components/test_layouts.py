"""
Tests complets pour src/ui/components/layouts.py
Couverture cible: >80%
"""

import pytest
from unittest.mock import patch, MagicMock


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DISPOSITION_GRILLE (grid_layout)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CARTE_ITEM (item_card)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


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
        
        carte_item(
            titre="Test",
            metadonnees=["info1", "info2"]
        )
        
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
        
        carte_item(
            titre="Test",
            metadonnees=["info"],
            statut="actif",
            couleur_statut="#4CAF50"
        )
        
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
        
        carte_item(
            titre="Test",
            metadonnees=[],
            url_image="http://example.com/img.jpg"
        )
        
        # Image devrait être appelée
        assert mock_cols.called


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION_PLIABLE (collapsible_section)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestSectionPliable:
    """Tests pour section_pliable()."""

    def test_section_pliable_import(self):
        """Test import réussi."""
        from src.ui.components.layouts import section_pliable
        assert callable(section_pliable)

    @patch("streamlit.expander")
    def test_section_pliable_basic(self, mock_expander):
        """Test section pliable basique."""
        from src.ui.components.layouts import section_pliable
        
        mock_expander.return_value.__enter__ = MagicMock()
        mock_expander.return_value.__exit__ = MagicMock()
        
        content_fn = MagicMock()
        
        section_pliable("Titre", content_fn)
        
        mock_expander.assert_called_once()
        content_fn.assert_called_once()

    @patch("streamlit.expander")
    def test_section_pliable_expanded(self, mock_expander):
        """Test section pliable ouverte."""
        from src.ui.components.layouts import section_pliable
        
        mock_expander.return_value.__enter__ = MagicMock()
        mock_expander.return_value.__exit__ = MagicMock()
        
        section_pliable("Titre", lambda: None, etendu=True)
        
        mock_expander.assert_called_with("Titre", expanded=True)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DISPOSITION_ONGLETS (tabs_layout)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestDispositionOnglets:
    """Tests pour disposition_onglets()."""

    def test_disposition_onglets_import(self):
        """Test import réussi."""
        from src.ui.components.layouts import disposition_onglets
        assert callable(disposition_onglets)

    @patch("streamlit.tabs")
    def test_disposition_onglets_basic(self, mock_tabs):
        """Test onglets basiques."""
        from src.ui.components.layouts import disposition_onglets
        
        tab1, tab2 = MagicMock(), MagicMock()
        tab1.__enter__ = MagicMock()
        tab1.__exit__ = MagicMock()
        tab2.__enter__ = MagicMock()
        tab2.__exit__ = MagicMock()
        mock_tabs.return_value = [tab1, tab2]
        
        content1, content2 = MagicMock(), MagicMock()
        
        disposition_onglets({
            "Tab1": content1,
            "Tab2": content2
        })
        
        mock_tabs.assert_called_with(["Tab1", "Tab2"])
        content1.assert_called_once()
        content2.assert_called_once()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONTENEUR_CARTE (card_container)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestConteneurCarte:
    """Tests pour conteneur_carte()."""

    def test_conteneur_carte_import(self):
        """Test import réussi."""
        from src.ui.components.layouts import conteneur_carte
        assert callable(conteneur_carte)

    @patch("streamlit.markdown")
    def test_conteneur_carte_basic(self, mock_markdown):
        """Test conteneur basique."""
        from src.ui.components.layouts import conteneur_carte
        
        content_fn = MagicMock()
        
        conteneur_carte(content_fn)
        
        assert mock_markdown.call_count == 2  # Début et fin div
        content_fn.assert_called_once()

    @patch("streamlit.markdown")
    def test_conteneur_carte_custom_color(self, mock_markdown):
        """Test conteneur avec couleur personnalisée."""
        from src.ui.components.layouts import conteneur_carte
        
        conteneur_carte(lambda: None, couleur="#f0f0f0")
        
        # Vérifie que la couleur est utilisée
        call_args = mock_markdown.call_args_list[0][0][0]
        assert "#f0f0f0" in call_args


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS D'INTÃ‰GRATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestLayoutsIntegration:
    """Tests d'intégration pour le module layouts."""

    def test_all_functions_exported(self):
        """Test que toutes les fonctions sont exportées."""
        from src.ui.components import layouts
        
        assert hasattr(layouts, "disposition_grille")
        assert hasattr(layouts, "carte_item")
        assert hasattr(layouts, "section_pliable")
        assert hasattr(layouts, "disposition_onglets")
        assert hasattr(layouts, "conteneur_carte")

    def test_imports_from_components(self):
        """Test imports depuis components."""
        from src.ui.components import (
            disposition_grille,
            carte_item,
            section_pliable,
            disposition_onglets,
            conteneur_carte,
        )
        
        assert callable(disposition_grille)
        assert callable(carte_item)
        assert callable(section_pliable)
        assert callable(disposition_onglets)
        assert callable(conteneur_carte)

    def test_imports_from_ui(self):
        """Test imports depuis ui."""
        from src.ui import (
            disposition_grille,
            carte_item,
            section_pliable,
            disposition_onglets,
            conteneur_carte,
        )
        
        assert callable(disposition_grille)
        assert callable(carte_item)
        assert callable(section_pliable)
        assert callable(disposition_onglets)
        assert callable(conteneur_carte)
