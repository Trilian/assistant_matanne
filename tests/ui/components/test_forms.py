"""
Tests complets pour src/ui/components/forms.py
Couverture cible: >80%
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date


# ═══════════════════════════════════════════════════════════
# CHAMP_FORMULAIRE (form_field)
# ═══════════════════════════════════════════════════════════


class TestChampFormulaire:
    """Tests pour champ_formulaire()."""

    def test_champ_formulaire_import(self):
        """Test import réussi."""
        from src.ui.components.forms import champ_formulaire
        assert callable(champ_formulaire)

    @patch("streamlit.text_input")
    def test_champ_formulaire_text(self, mock_input):
        """Test champ texte."""
        from src.ui.components.forms import champ_formulaire
        
        mock_input.return_value = "valeur"
        
        config = {"type": "text", "name": "nom", "label": "Nom", "default": ""}
        result = champ_formulaire(config, "prefix")
        
        mock_input.assert_called_once()
        assert result == "valeur"

    @patch("streamlit.text_input")
    def test_champ_formulaire_required(self, mock_input):
        """Test champ requis ajoute *."""
        from src.ui.components.forms import champ_formulaire
        
        config = {"type": "text", "name": "nom", "label": "Nom", "required": True}
        champ_formulaire(config, "prefix")
        
        # Vérifie que le label contient *
        call_args = mock_input.call_args[0][0]
        assert "*" in call_args

    @patch("streamlit.number_input")
    def test_champ_formulaire_number(self, mock_input):
        """Test champ numérique."""
        from src.ui.components.forms import champ_formulaire
        
        mock_input.return_value = 42.0
        
        config = {"type": "number", "name": "age", "label": "Âge", "default": 0}
        result = champ_formulaire(config, "prefix")
        
        mock_input.assert_called_once()
        assert result == 42.0

    @patch("streamlit.selectbox")
    def test_champ_formulaire_select(self, mock_select):
        """Test champ select."""
        from src.ui.components.forms import champ_formulaire
        
        mock_select.return_value = "option1"
        
        config = {"type": "select", "name": "choix", "label": "Choix", "options": ["option1", "option2"]}
        result = champ_formulaire(config, "prefix")
        
        mock_select.assert_called_once()
        assert result == "option1"

    @patch("streamlit.multiselect")
    def test_champ_formulaire_multiselect(self, mock_multi):
        """Test champ multiselect."""
        from src.ui.components.forms import champ_formulaire
        
        mock_multi.return_value = ["a", "b"]
        
        config = {"type": "multiselect", "name": "tags", "label": "Tags", "options": ["a", "b", "c"]}
        result = champ_formulaire(config, "prefix")
        
        mock_multi.assert_called_once()
        assert result == ["a", "b"]

    @patch("streamlit.checkbox")
    def test_champ_formulaire_checkbox(self, mock_check):
        """Test champ checkbox."""
        from src.ui.components.forms import champ_formulaire
        
        mock_check.return_value = True
        
        config = {"type": "checkbox", "name": "actif", "label": "Actif", "default": False}
        result = champ_formulaire(config, "prefix")
        
        mock_check.assert_called_once()
        assert result is True

    @patch("streamlit.text_area")
    def test_champ_formulaire_textarea(self, mock_area):
        """Test champ textarea."""
        from src.ui.components.forms import champ_formulaire
        
        mock_area.return_value = "long texte"
        
        config = {"type": "textarea", "name": "description", "label": "Description"}
        result = champ_formulaire(config, "prefix")
        
        mock_area.assert_called_once()
        assert result == "long texte"

    @patch("streamlit.date_input")
    def test_champ_formulaire_date(self, mock_date):
        """Test champ date."""
        from src.ui.components.forms import champ_formulaire
        
        test_date = date(2024, 1, 15)
        mock_date.return_value = test_date
        
        config = {"type": "date", "name": "naissance", "label": "Date de naissance"}
        result = champ_formulaire(config, "prefix")
        
        mock_date.assert_called_once()
        assert result == test_date

    @patch("streamlit.slider")
    def test_champ_formulaire_slider(self, mock_slider):
        """Test champ slider."""
        from src.ui.components.forms import champ_formulaire
        
        mock_slider.return_value = 75
        
        config = {"type": "slider", "name": "niveau", "label": "Niveau", "min": 0, "max": 100, "default": 50}
        result = champ_formulaire(config, "prefix")
        
        mock_slider.assert_called_once()
        assert result == 75

    @patch("streamlit.text_input")
    def test_champ_formulaire_unknown_type(self, mock_input):
        """Test type inconnu -> text_input."""
        from src.ui.components.forms import champ_formulaire
        
        mock_input.return_value = "fallback"
        
        config = {"type": "unknown", "name": "champ", "label": "Champ"}
        result = champ_formulaire(config, "prefix")
        
        mock_input.assert_called_once()
        assert result == "fallback"


# ═══════════════════════════════════════════════════════════
# BARRE_RECHERCHE (search_bar)
# ═══════════════════════════════════════════════════════════


class TestBarreRecherche:
    """Tests pour barre_recherche()."""

    def test_barre_recherche_import(self):
        """Test import réussi."""
        from src.ui.components.forms import barre_recherche
        assert callable(barre_recherche)

    @patch("streamlit.text_input")
    def test_barre_recherche_default(self, mock_input):
        """Test barre recherche par défaut."""
        from src.ui.components.forms import barre_recherche
        
        mock_input.return_value = ""
        
        result = barre_recherche()
        
        mock_input.assert_called_once()
        # Vérifie placeholder contient emoji recherche
        call_kwargs = mock_input.call_args[1]
        assert "🔍" in call_kwargs.get("placeholder", "")

    @patch("streamlit.text_input")
    def test_barre_recherche_custom_placeholder(self, mock_input):
        """Test placeholder personnalisé."""
        from src.ui.components.forms import barre_recherche
        
        mock_input.return_value = "test"
        
        result = barre_recherche(texte_indicatif="Rechercher recettes...", cle="recipe_search")
        
        call_kwargs = mock_input.call_args[1]
        assert "recettes" in call_kwargs.get("placeholder", "")
        assert call_kwargs.get("key") == "recipe_search"

    @patch("streamlit.text_input")
    def test_barre_recherche_returns_string(self, mock_input):
        """Test retourne une chaîne."""
        from src.ui.components.forms import barre_recherche
        
        mock_input.return_value = "terme recherche"
        
        result = barre_recherche()
        
        assert isinstance(result, str)
        assert result == "terme recherche"


# ═══════════════════════════════════════════════════════════
# PANNEAU_FILTRES (filter_panel)
# ═══════════════════════════════════════════════════════════


class TestPanneauFiltres:
    """Tests pour panneau_filtres()."""

    def test_panneau_filtres_import(self):
        """Test import réussi."""
        from src.ui.components.forms import panneau_filtres
        assert callable(panneau_filtres)

    @patch("streamlit.selectbox")
    def test_panneau_filtres_single(self, mock_select):
        """Test avec un seul filtre."""
        from src.ui.components.forms import panneau_filtres
        
        mock_select.return_value = "été"
        
        config = {
            "saison": {
                "type": "select",
                "label": "Saison",
                "options": ["Toutes", "été", "hiver"]
            }
        }
        
        result = panneau_filtres(config, "recipe")
        
        assert "saison" in result
        assert result["saison"] == "été"

    @patch("streamlit.selectbox")
    @patch("streamlit.checkbox")
    def test_panneau_filtres_multiple(self, mock_check, mock_select):
        """Test avec plusieurs filtres."""
        from src.ui.components.forms import panneau_filtres
        
        mock_select.return_value = "facile"
        mock_check.return_value = True
        
        config = {
            "difficulte": {"type": "select", "label": "Difficulté", "options": ["facile", "moyen"]},
            "vegetarien": {"type": "checkbox", "label": "Végétarien"}
        }
        
        result = panneau_filtres(config, "recipe")
        
        assert len(result) == 2

    def test_panneau_filtres_empty(self):
        """Test avec config vide."""
        from src.ui.components.forms import panneau_filtres
        
        result = panneau_filtres({}, "prefix")
        
        assert result == {}


# ═══════════════════════════════════════════════════════════
# FILTRES_RAPIDES (quick_filters)
# ═══════════════════════════════════════════════════════════


class TestFiltresRapides:
    """Tests pour filtres_rapides()."""

    def test_filtres_rapides_import(self):
        """Test import réussi."""
        from src.ui.components.forms import filtres_rapides
        assert callable(filtres_rapides)

    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=False)
    def test_filtres_rapides_no_selection(self, mock_btn, mock_cols):
        """Test sans sélection."""
        from src.ui.components.forms import filtres_rapides
        
        mock_cols.return_value = [MagicMock(), MagicMock(), MagicMock()]
        
        filters = {"Type": ["Tous", "Entrée", "Plat"]}
        
        result = filtres_rapides(filters)
        
        assert result == {}

    @patch("streamlit.columns")
    @patch("streamlit.button")
    def test_filtres_rapides_with_selection(self, mock_btn, mock_cols):
        """Test avec sélection."""
        from src.ui.components.forms import filtres_rapides
        
        mock_cols.return_value = [MagicMock(), MagicMock()]
        # Premier bouton cliqué, deuxième non
        mock_btn.side_effect = [True, False]
        
        filters = {"Type": ["Entrée", "Plat"]}
        
        result = filtres_rapides(filters, prefixe_cle="test")
        
        assert "Type" in result
        assert result["Type"] == "Entrée"

    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=False)
    def test_filtres_rapides_multiple_groups(self, mock_btn, mock_cols):
        """Test avec plusieurs groupes."""
        from src.ui.components.forms import filtres_rapides
        
        mock_cols.return_value = [MagicMock(), MagicMock()]
        
        filters = {
            "Type": ["A", "B"],
            "Status": ["X", "Y"]
        }
        
        result = filtres_rapides(filters)
        
        # Vérifie que columns est appelé pour chaque groupe
        assert mock_cols.call_count == 2


# ═══════════════════════════════════════════════════════════
# TESTS D'INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestFormsIntegration:
    """Tests d'intégration pour le module forms."""

    def test_all_functions_exported(self):
        """Test que toutes les fonctions sont exportées."""
        from src.ui.components import forms
        
        assert hasattr(forms, "champ_formulaire")
        assert hasattr(forms, "barre_recherche")
        assert hasattr(forms, "panneau_filtres")
        assert hasattr(forms, "filtres_rapides")

    def test_imports_from_components(self):
        """Test imports depuis components."""
        from src.ui.components import (
            champ_formulaire,
            barre_recherche,
            panneau_filtres,
            filtres_rapides,
        )
        
        assert callable(champ_formulaire)
        assert callable(barre_recherche)
        assert callable(panneau_filtres)
        assert callable(filtres_rapides)

    def test_imports_from_ui(self):
        """Test imports depuis ui."""
        from src.ui import (
            champ_formulaire,
            barre_recherche,
            panneau_filtres,
            filtres_rapides,
        )
        
        assert callable(champ_formulaire)
        assert callable(barre_recherche)
        assert callable(panneau_filtres)
        assert callable(filtres_rapides)
