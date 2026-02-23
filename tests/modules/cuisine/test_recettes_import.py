"""
Tests pour src/modules/cuisine/recettes_import.py

Tests pour l import de recettes depuis URL, PDF et texte.
"""

from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


class SessionStateMock(dict):
    """Mock for st.session_state"""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


def setup_mock_st(mock_st: MagicMock, session_data: dict | None = None) -> None:
    """Setup mock streamlit"""

    def mock_columns(n, **kwargs):
        count = n if isinstance(n, int) else len(n)
        return [MagicMock() for _ in range(count)]

    mock_st.columns.side_effect = mock_columns
    mock_st.session_state = SessionStateMock(session_data or {})
    mock_st.tabs.return_value = [MagicMock() for _ in range(3)]
    mock_st.button.return_value = False
    mock_st.form.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.form_submit_button.return_value = False
    mock_st.text_input.return_value = ""
    mock_st.text_area.return_value = ""
    mock_st.number_input.return_value = 4
    mock_st.selectbox.return_value = "diner"
    mock_st.file_uploader.return_value = None


class TestImports:
    """Tests d import des fonctions"""

    def test_import_render_importer(self):
        """Test import afficher_importer"""
        from src.modules.cuisine.recettes_import import afficher_importer

        assert callable(afficher_importer)

    def test_import_render_import_url(self):
        """Test import _afficher_import_url"""
        from src.modules.cuisine.recettes_import import _afficher_import_url

        assert callable(_afficher_import_url)

    def test_import_render_import_pdf(self):
        """Test import _afficher_import_pdf"""
        from src.modules.cuisine.recettes_import import _afficher_import_pdf

        assert callable(_afficher_import_pdf)

    def test_import_render_import_text(self):
        """Test import _afficher_import_text"""
        from src.modules.cuisine.recettes_import import _afficher_import_text

        assert callable(_afficher_import_text)

    def test_import_show_import_preview(self):
        """Test import _show_import_preview"""
        from src.modules.cuisine.recettes_import import _show_import_preview

        assert callable(_show_import_preview)


@pytest.mark.unit
class TestRenderImporter:
    """Tests pour afficher_importer"""

    @patch("src.modules.cuisine.recettes_import.st")
    def test_render_importer_basic(self, mock_st):
        """Test afficher_importer s execute sans erreur"""
        from src.modules.cuisine.recettes_import import afficher_importer

        setup_mock_st(mock_st)
        afficher_importer()
        mock_st.subheader.assert_called_once()
        mock_st.tabs.assert_called_once()


@pytest.mark.unit
class TestRenderImportUrl:
    """Tests pour _afficher_import_url"""

    @patch("src.modules.cuisine.recettes_import.st")
    def test_render_import_url_basic(self, mock_st):
        """Test afficher_import_url sans action"""
        from src.modules.cuisine.recettes_import import _afficher_import_url

        setup_mock_st(mock_st)
        _afficher_import_url()
        mock_st.markdown.assert_called()
        mock_st.text_input.assert_called()

    @patch("src.modules.cuisine.recettes_import.st")
    def test_render_import_url_no_url_error(self, mock_st):
        """Test afficher_import_url avec bouton mais pas d URL"""
        from src.modules.cuisine.recettes_import import _afficher_import_url

        setup_mock_st(mock_st)
        mock_st.button.return_value = True
        mock_st.text_input.return_value = ""

        _afficher_import_url()
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes_import.get_recipe_import_service")
    @patch("src.modules.cuisine.recettes_import.st")
    def test_render_import_url_extract_success(self, mock_st, mock_factory):
        """Test extraction reussie depuis URL"""
        from src.modules.cuisine.recettes_import import _afficher_import_url

        setup_mock_st(mock_st, {"extracted_recipe": None})
        mock_st.button.return_value = True
        mock_st.text_input.return_value = "https://example.com/recette"

        # Mock le service et son résultat
        mock_service = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.recipe = MagicMock()
        mock_result.recipe.model_dump.return_value = {"nom": "Test Recette"}
        mock_result.recipe.ingredients = []
        mock_service.import_from_url.return_value = mock_result
        mock_factory.return_value = mock_service

        _afficher_import_url()
        mock_service.import_from_url.assert_called_once_with("https://example.com/recette")
        mock_st.success.assert_called()

    @patch("src.modules.cuisine.recettes_import.get_recipe_import_service")
    @patch("src.modules.cuisine.recettes_import.st")
    def test_render_import_url_extract_failure(self, mock_st, mock_factory):
        """Test extraction echouee depuis URL"""
        from src.modules.cuisine.recettes_import import _afficher_import_url

        setup_mock_st(mock_st, {"extracted_recipe": None})
        mock_st.button.return_value = True
        mock_st.text_input.return_value = "https://example.com/recette"

        # Mock le service retournant un échec
        mock_service = MagicMock()
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.recipe = None
        mock_result.message = "Extraction impossible"
        mock_service.import_from_url.return_value = mock_result
        mock_factory.return_value = mock_service

        _afficher_import_url()
        mock_st.error.assert_called()


@pytest.mark.unit
class TestRenderImportPdf:
    """Tests pour _afficher_import_pdf"""

    @patch("src.modules.cuisine.recettes_import.st")
    def test_render_import_pdf_basic(self, mock_st):
        """Test afficher_import_pdf sans fichier"""
        from src.modules.cuisine.recettes_import import _afficher_import_pdf

        setup_mock_st(mock_st)
        mock_st.file_uploader.return_value = None

        _afficher_import_pdf()
        mock_st.markdown.assert_called()
        mock_st.file_uploader.assert_called()


@pytest.mark.unit
class TestRenderImportText:
    """Tests pour _afficher_import_text"""

    @patch("src.modules.cuisine.recettes_import.st")
    def test_render_import_text_basic(self, mock_st):
        """Test afficher_import_text sans action"""
        from src.modules.cuisine.recettes_import import _afficher_import_text

        setup_mock_st(mock_st)
        _afficher_import_text()
        mock_st.markdown.assert_called()
        mock_st.text_area.assert_called()

    @patch("src.modules.cuisine.recettes_import.st")
    def test_render_import_text_no_text_error(self, mock_st):
        """Test afficher_import_text avec bouton mais pas de texte"""
        from src.modules.cuisine.recettes_import import _afficher_import_text

        setup_mock_st(mock_st)
        mock_st.button.return_value = True
        mock_st.text_area.return_value = ""

        _afficher_import_text()
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.recettes_import.RecipeImporter")
    @patch("src.modules.cuisine.recettes_import.st")
    def test_render_import_text_extract_success(self, mock_st, mock_importer):
        """Test extraction reussie depuis texte"""
        from src.modules.cuisine.recettes_import import _afficher_import_text

        setup_mock_st(mock_st)
        mock_st.button.return_value = True
        mock_st.text_area.return_value = "Ma recette\nIngredients:\n- 1 item"
        mock_importer.from_text.return_value = {"nom": "Ma recette", "ingredients": ["1 item"]}

        _afficher_import_text()
        mock_importer.from_text.assert_called_once()
        mock_st.success.assert_called()


@pytest.mark.unit
class TestShowImportPreview:
    """Tests pour _show_import_preview"""

    @patch("src.modules.cuisine.recettes_import.st")
    def test_show_import_preview_basic(self, mock_st):
        """Test show_import_preview avec donnees basiques"""
        from src.modules.cuisine.recettes_import import _show_import_preview

        setup_mock_st(mock_st, {"last_imported_recipe_name": None})
        recipe_data = {
            "nom": "Test Recette",
            "description": "Une recette test",
            "ingredients": ["item1", "item2"],
            "etapes": ["etape 1", "etape 2"],
            "temps_preparation": 15,
            "temps_cuisson": 30,
            "portions": 4,
        }

        _show_import_preview(recipe_data)
        mock_st.form.assert_called()

    @patch("src.modules.cuisine.recettes_import.st")
    def test_show_import_preview_with_image_url(self, mock_st):
        """Test show_import_preview avec URL image"""
        from src.modules.cuisine.recettes_import import _show_import_preview

        setup_mock_st(mock_st, {"last_imported_recipe_name": None})
        recipe_data = {
            "nom": "Recette avec image",
            "image_url": "https://example.com/image.jpg",
            "ingredients": ["item"],
            "etapes": ["etape"],
        }

        _show_import_preview(recipe_data)
        mock_st.text_input.assert_called()

    @patch("src.modules.cuisine.recettes_import.st")
    def test_show_import_preview_type_detection_dessert(self, mock_st):
        """Test detection automatique type dessert"""
        from src.modules.cuisine.recettes_import import _show_import_preview

        setup_mock_st(mock_st, {"last_imported_recipe_name": None})
        mock_st.text_input.return_value = "Gateau au chocolat"
        recipe_data = {"nom": "Gateau au chocolat", "ingredients": [], "etapes": []}

        _show_import_preview(recipe_data)
        mock_st.selectbox.assert_called()

    @patch("src.modules.cuisine.recettes_import.st")
    def test_show_import_preview_last_imported_shown(self, mock_st):
        """Test affichage message succes apres import"""
        from src.modules.cuisine.recettes_import import _show_import_preview

        setup_mock_st(mock_st, {"last_imported_recipe_name": "Recette importee"})
        recipe_data = {"nom": "Autre recette", "ingredients": [], "etapes": []}

        _show_import_preview(recipe_data)
        mock_st.success.assert_called()
