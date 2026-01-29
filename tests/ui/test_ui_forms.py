"""
Tests pour src/ui/components/forms.py
Champs formulaire, recherche, filtres
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_streamlit():
    """Mock complet de Streamlit"""
    with patch("src.ui.components.forms.st") as mock_st:
        # Configuration mocks pour retourner des valeurs
        mock_st.text_input.return_value = "test_value"
        mock_st.number_input.return_value = 42.0
        mock_st.selectbox.return_value = "option1"
        mock_st.multiselect.return_value = ["opt1", "opt2"]
        mock_st.checkbox.return_value = True
        mock_st.text_area.return_value = "text area content"
        mock_st.date_input.return_value = date(2026, 1, 28)
        mock_st.slider.return_value = 75
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.return_value = False
        yield mock_st


# ═══════════════════════════════════════════════════════════
# TESTS FORM_FIELD
# ═══════════════════════════════════════════════════════════


class TestFormField:
    """Tests pour form_field()"""

    def test_text_field(self, mock_streamlit):
        """Test champ texte"""
        from src.ui.components.forms import form_field

        config = {"type": "text", "name": "nom", "label": "Nom", "default": "default_val"}

        result = form_field(config, "test")

        mock_streamlit.text_input.assert_called_once()
        assert result == "test_value"

    def test_text_field_required(self, mock_streamlit):
        """Test champ texte requis"""
        from src.ui.components.forms import form_field

        config = {"type": "text", "name": "nom", "label": "Nom", "required": True}

        form_field(config, "test")

        # Vérifier que le label contient *
        call_args = mock_streamlit.text_input.call_args
        assert " *" in call_args[0][0]

    def test_number_field(self, mock_streamlit):
        """Test champ nombre"""
        from src.ui.components.forms import form_field

        config = {
            "type": "number",
            "name": "age",
            "label": "Âge",
            "default": 25,
            "min": 0,
            "max": 120,
            "step": 1,
        }

        result = form_field(config, "test")

        mock_streamlit.number_input.assert_called_once()
        assert result == 42.0

    def test_select_field(self, mock_streamlit):
        """Test champ select"""
        from src.ui.components.forms import form_field

        config = {
            "type": "select",
            "name": "categorie",
            "label": "Catégorie",
            "options": ["Entrée", "Plat", "Dessert"],
        }

        result = form_field(config, "test")

        mock_streamlit.selectbox.assert_called_once()
        assert result == "option1"

    def test_multiselect_field(self, mock_streamlit):
        """Test champ multiselect"""
        from src.ui.components.forms import form_field

        config = {
            "type": "multiselect",
            "name": "tags",
            "label": "Tags",
            "options": ["Végétarien", "Rapide", "Facile"],
        }

        result = form_field(config, "test")

        mock_streamlit.multiselect.assert_called_once()
        assert result == ["opt1", "opt2"]

    def test_checkbox_field(self, mock_streamlit):
        """Test champ checkbox"""
        from src.ui.components.forms import form_field

        config = {"type": "checkbox", "name": "actif", "label": "Actif", "default": False}

        result = form_field(config, "test")

        mock_streamlit.checkbox.assert_called_once()
        assert result is True

    def test_textarea_field(self, mock_streamlit):
        """Test champ textarea"""
        from src.ui.components.forms import form_field

        config = {
            "type": "textarea",
            "name": "description",
            "label": "Description",
            "default": "",
        }

        result = form_field(config, "test")

        mock_streamlit.text_area.assert_called_once()
        assert result == "text area content"

    def test_date_field(self, mock_streamlit):
        """Test champ date"""
        from src.ui.components.forms import form_field

        config = {"type": "date", "name": "date_debut", "label": "Date début"}

        result = form_field(config, "test")

        mock_streamlit.date_input.assert_called_once()
        assert result == date(2026, 1, 28)

    def test_slider_field(self, mock_streamlit):
        """Test champ slider"""
        from src.ui.components.forms import form_field

        config = {
            "type": "slider",
            "name": "niveau",
            "label": "Niveau",
            "min": 0,
            "max": 100,
            "default": 50,
        }

        result = form_field(config, "test")

        mock_streamlit.slider.assert_called_once()
        assert result == 75

    def test_unknown_field_type_defaults_to_text(self, mock_streamlit):
        """Test type inconnu -> text_input par défaut"""
        from src.ui.components.forms import form_field

        config = {"type": "unknown_type", "name": "field", "label": "Field"}

        result = form_field(config, "test")

        # Doit utiliser text_input comme fallback
        mock_streamlit.text_input.assert_called()
        assert result == "test_value"

    def test_field_default_values(self, mock_streamlit):
        """Test valeurs par défaut des champs"""
        from src.ui.components.forms import form_field

        # Config minimale
        config = {"name": "field"}

        form_field(config, "prefix")

        # Doit utiliser text_input par défaut
        mock_streamlit.text_input.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS SEARCH_BAR
# ═══════════════════════════════════════════════════════════


class TestSearchBar:
    """Tests pour search_bar()"""

    def test_search_bar_default(self, mock_streamlit):
        """Test barre de recherche par défaut"""
        from src.ui.components.forms import search_bar

        mock_streamlit.text_input.return_value = "recherche"

        result = search_bar()

        mock_streamlit.text_input.assert_called_once()
        call_kwargs = mock_streamlit.text_input.call_args[1]
        assert "🔍" in call_kwargs["placeholder"]
        assert call_kwargs["label_visibility"] == "collapsed"
        assert result == "recherche"

    def test_search_bar_custom_placeholder(self, mock_streamlit):
        """Test placeholder personnalisé"""
        from src.ui.components.forms import search_bar

        search_bar(placeholder="Rechercher recettes...")

        call_kwargs = mock_streamlit.text_input.call_args[1]
        assert "Rechercher recettes..." in call_kwargs["placeholder"]

    def test_search_bar_custom_key(self, mock_streamlit):
        """Test clé personnalisée"""
        from src.ui.components.forms import search_bar

        search_bar(key="recipe_search")

        call_kwargs = mock_streamlit.text_input.call_args[1]
        assert call_kwargs["key"] == "recipe_search"


# ═══════════════════════════════════════════════════════════
# TESTS FILTER_PANEL
# ═══════════════════════════════════════════════════════════


class TestFilterPanel:
    """Tests pour filter_panel()"""

    def test_filter_panel_single_filter(self, mock_streamlit):
        """Test panneau avec un filtre"""
        from src.ui.components.forms import filter_panel

        filters_config = {"saison": {"type": "select", "label": "Saison", "options": ["Toutes", "Été", "Hiver"]}}

        result = filter_panel(filters_config, "recipe")

        assert "saison" in result

    def test_filter_panel_multiple_filters(self, mock_streamlit):
        """Test panneau avec plusieurs filtres"""
        from src.ui.components.forms import filter_panel

        filters_config = {
            "saison": {"type": "select", "label": "Saison", "options": ["Toutes"]},
            "difficulte": {"type": "select", "label": "Difficulté", "options": ["Facile", "Moyen"]},
            "actif": {"type": "checkbox", "label": "Actif seulement"},
        }

        result = filter_panel(filters_config, "recipe")

        assert len(result) == 3
        assert "saison" in result
        assert "difficulte" in result
        assert "actif" in result

    def test_filter_panel_empty(self, mock_streamlit):
        """Test panneau vide"""
        from src.ui.components.forms import filter_panel

        result = filter_panel({}, "test")

        assert result == {}


# ═══════════════════════════════════════════════════════════
# TESTS QUICK_FILTERS
# ═══════════════════════════════════════════════════════════


class TestQuickFilters:
    """Tests pour quick_filters()"""

    def test_quick_filters_no_selection(self, mock_streamlit):
        """Test filtres rapides sans sélection"""
        from src.ui.components.forms import quick_filters

        mock_streamlit.button.return_value = False
        # Mock columns avec 4 éléments
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=None)
        mock_col.__exit__ = MagicMock(return_value=None)
        mock_streamlit.columns.return_value = [mock_col, mock_col, mock_col, mock_col]

        filters = {"Type": ["Tous", "Entrée", "Plat", "Dessert"]}

        result = quick_filters(filters)

        # Pas de sélection car button retourne False
        assert result == {}

    def test_quick_filters_with_selection(self, mock_streamlit):
        """Test filtres rapides avec sélection"""
        from src.ui.components.forms import quick_filters

        # Premier bouton sélectionné
        mock_streamlit.button.side_effect = [True, False, False, False]
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=None)
        mock_col.__exit__ = MagicMock(return_value=None)
        mock_streamlit.columns.return_value = [mock_col, mock_col, mock_col, mock_col]

        filters = {"Type": ["Tous", "Entrée", "Plat", "Dessert"]}

        result = quick_filters(filters)

        assert "Type" in result
        assert result["Type"] == "Tous"

    def test_quick_filters_multiple_groups(self, mock_streamlit):
        """Test filtres rapides avec plusieurs groupes"""
        from src.ui.components.forms import quick_filters

        mock_streamlit.button.return_value = False
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=None)
        mock_col.__exit__ = MagicMock(return_value=None)
        mock_streamlit.columns.return_value = [mock_col, mock_col, mock_col]

        filters = {
            "Type": ["Tous", "Entrée", "Plat"],
            "Difficulté": ["Facile", "Moyen", "Difficile"],
        }

        result = quick_filters(filters, key_prefix="custom")

        # columns appelé deux fois (une par groupe)
        assert mock_streamlit.columns.call_count == 2

    def test_quick_filters_custom_key_prefix(self, mock_streamlit):
        """Test préfixe de clé personnalisé"""
        from src.ui.components.forms import quick_filters

        mock_streamlit.button.return_value = False
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=None)
        mock_col.__exit__ = MagicMock(return_value=None)
        mock_streamlit.columns.return_value = [mock_col, mock_col]

        quick_filters({"Groupe": ["A", "B"]}, key_prefix="my_prefix")

        # Vérifier que les boutons utilisent le préfixe
        call_args = mock_streamlit.button.call_args_list
        for call in call_args:
            assert "my_prefix" in call[1]["key"]
