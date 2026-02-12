"""
Tests Ã©tendus pour couverture UI 80%+

Couvre:
- FormBuilder (base_form.py)
- Modal, DynamicList, Stepper (dynamic.py)
- Layout: header, footer, sidebar
- Domain UI
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import date


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FORM BUILDER (base_form.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFormBuilder:
    """Tests pour FormBuilder."""
    
    def test_form_builder_init(self):
        """Test initialisation FormBuilder."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test_form", title="Test")
        assert form.form_id == "test_form"
        assert form.title == "Test"
        assert form.fields == []
    
    def test_add_text(self):
        """Test ajout champ texte."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        result = form.add_text("nom", "Nom", required=True)
        
        assert result is form  # Fluent interface
        assert len(form.fields) == 1
        assert form.fields[0]["type"] == "text"
        assert "*" in form.fields[0]["label"]
    
    def test_add_textarea(self):
        """Test ajout textarea."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.add_textarea("desc", "Description", height=150)
        
        assert form.fields[0]["type"] == "textarea"
        assert form.fields[0]["height"] == 150
    
    def test_add_number(self):
        """Test ajout champ nombre."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.add_number("qty", "QuantitÃ©", min_value=0, max_value=100, step=5)
        
        assert form.fields[0]["type"] == "number"
        assert form.fields[0]["min_value"] == 0
        assert form.fields[0]["max_value"] == 100
    
    def test_add_select(self):
        """Test ajout select."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.add_select("cat", "CatÃ©gorie", options=["A", "B", "C"])
        
        assert form.fields[0]["type"] == "select"
        assert form.fields[0]["options"] == ["A", "B", "C"]
    
    def test_add_multiselect(self):
        """Test ajout multiselect."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.add_multiselect("tags", "Tags", options=["x", "y"])
        
        assert form.fields[0]["type"] == "multiselect"
        assert form.fields[0]["default"] == []
    
    def test_add_checkbox(self):
        """Test ajout checkbox."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.add_checkbox("active", "Actif", default=True)
        
        assert form.fields[0]["type"] == "checkbox"
        assert form.fields[0]["default"] is True
    
    def test_add_date(self):
        """Test ajout date."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.add_date("date", "Date")
        
        assert form.fields[0]["type"] == "date"
        assert form.fields[0]["default"] == date.today()
    
    def test_add_slider(self):
        """Test ajout slider."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.add_slider("rating", "Note", min_value=1, max_value=5, default=3)
        
        assert form.fields[0]["type"] == "slider"
        assert form.fields[0]["default"] == 3
    
    def test_add_divider(self):
        """Test ajout divider."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.add_divider()
        
        assert form.fields[0]["type"] == "divider"
    
    def test_add_header(self):
        """Test ajout header."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.add_header("Section 1")
        
        assert form.fields[0]["type"] == "header"
        assert form.fields[0]["text"] == "Section 1"
    
    def test_fluent_interface(self):
        """Test chaÃ®nage de mÃ©thodes."""
        from src.ui.core.base_form import FormBuilder
        
        form = (
            FormBuilder("test", "Mon Form")
            .add_text("nom", "Nom")
            .add_number("age", "Ã‚ge")
            .add_divider()
            .add_checkbox("ok", "OK")
        )
        
        assert len(form.fields) == 4
    
    @patch('src.ui.core.base_form.st')
    def test_render_form(self, mock_st):
        """Test render du formulaire."""
        mock_form = MagicMock()
        mock_form.__enter__ = MagicMock(return_value=mock_form)
        mock_form.__exit__ = MagicMock(return_value=False)
        mock_st.form = MagicMock(return_value=mock_form)
        mock_st.markdown = MagicMock()
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[mock_col, mock_col])
        mock_st.form_submit_button = MagicMock(return_value=False)
        mock_st.text_input = MagicMock(return_value="")
        
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test", "Test Form")
        form.add_text("nom", "Nom")
        
        result = form.render()
        
        mock_st.form.assert_called_with("test")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODAL (dynamic.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestModal:
    """Tests pour Modal."""
    
    @patch('src.ui.components.dynamic.st')
    def test_modal_init(self, mock_st):
        """Test initialisation Modal."""
        mock_st.session_state = {}
        
        from src.ui.components.dynamic import Modal
        
        modal = Modal("test")
        assert modal.key == "modal_test"
    
    @patch('src.ui.components.dynamic.st')
    def test_modal_show(self, mock_st):
        """Test afficher modal."""
        mock_st.session_state = {}
        
        from src.ui.components.dynamic import Modal
        
        modal = Modal("test")
        modal.show()
        
        assert mock_st.session_state["modal_test"] is True
    
    @patch('src.ui.components.dynamic.st')
    def test_modal_is_showing_false(self, mock_st):
        """Test modal pas visible."""
        mock_st.session_state = {"modal_test": False}
        
        from src.ui.components.dynamic import Modal
        
        modal = Modal("test")
        assert modal.is_showing() is False
    
    @patch('src.ui.components.dynamic.st')
    def test_modal_is_showing_true(self, mock_st):
        """Test modal visible."""
        mock_st.session_state = {"modal_test": True}
        
        from src.ui.components.dynamic import Modal
        
        modal = Modal("test")
        assert modal.is_showing() is True
    
    @patch('src.ui.components.dynamic.st')
    def test_modal_confirm(self, mock_st):
        """Test bouton confirmer."""
        mock_st.session_state = {}
        mock_st.button = MagicMock(return_value=True)
        
        from src.ui.components.dynamic import Modal
        
        modal = Modal("test")
        result = modal.confirm()
        
        assert result is True
        mock_st.button.assert_called()
    
    @patch('src.ui.components.dynamic.st')
    def test_modal_cancel(self, mock_st):
        """Test bouton annuler."""
        mock_st.session_state = {"modal_test": True}
        mock_st.button = MagicMock(return_value=False)
        mock_st.rerun = MagicMock()
        
        from src.ui.components.dynamic import Modal
        
        modal = Modal("test")
        modal.cancel()  # Ne devrait pas fermer car button retourne False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS DYNAMIC LIST (dynamic.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestDynamicList:
    """Tests pour DynamicList."""
    
    @patch('src.ui.components.dynamic.st')
    def test_dynamic_list_init(self, mock_st):
        """Test initialisation DynamicList."""
        mock_st.session_state = {}
        
        from src.ui.components.dynamic import DynamicList
        
        fields = [{"name": "nom", "label": "Nom", "type": "text"}]
        dl = DynamicList("test", fields)
        
        assert dl.key == "test"
        assert dl.fields == fields
    
    @patch('src.ui.components.dynamic.st')
    def test_dynamic_list_init_with_items(self, mock_st):
        """Test init avec items."""
        mock_st.session_state = {}
        
        from src.ui.components.dynamic import DynamicList
        
        fields = [{"name": "nom", "type": "text"}]
        initial = [{"nom": "Item 1"}]
        dl = DynamicList("test", fields, initial_items=initial)
        
        assert mock_st.session_state["test_items"] == initial
    
    @patch('src.ui.components.dynamic.st')
    def test_dynamic_list_get_items(self, mock_st):
        """Test rÃ©cupÃ©ration items."""
        mock_st.session_state = {"test_items": [{"a": 1}]}
        
        from src.ui.components.dynamic import DynamicList
        
        fields = [{"name": "a", "type": "text"}]
        dl = DynamicList("test", fields)
        
        items = dl.get_items()
        assert items == [{"a": 1}]
    
    @patch('src.ui.components.dynamic.st')
    def test_dynamic_list_clear(self, mock_st):
        """Test vider liste."""
        mock_st.session_state = {"test_items": [{"a": 1}]}
        
        from src.ui.components.dynamic import DynamicList
        
        fields = [{"name": "a", "type": "text"}]
        dl = DynamicList("test", fields)
        dl.clear()
        
        assert mock_st.session_state["test_items"] == []
    
    @patch('src.ui.components.dynamic.st')
    def test_dynamic_list_add_item(self, mock_st):
        """Test ajout item."""
        mock_st.session_state = {"test_items": []}
        
        from src.ui.components.dynamic import DynamicList
        
        fields = [{"name": "nom", "type": "text"}]
        dl = DynamicList("test", fields)
        dl.add_item({"nom": "New"})
        
        assert len(mock_st.session_state["test_items"]) == 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS STEPPER (dynamic.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestStepper:
    """Tests pour Stepper."""
    
    @patch('src.ui.components.dynamic.st')
    def test_stepper_init(self, mock_st):
        """Test initialisation Stepper."""
        mock_st.session_state = {}
        
        from src.ui.components.dynamic import Stepper
        
        stepper = Stepper("wizard", ["Ã‰tape 1", "Ã‰tape 2", "Ã‰tape 3"])
        
        assert stepper.key == "wizard"
        assert len(stepper.steps) == 3
    
    @patch('src.ui.components.dynamic.st')
    def test_stepper_render(self, mock_st):
        """Test render stepper."""
        mock_st.session_state = {"wizard_step": 0}
        mock_st.progress = MagicMock()
        mock_st.markdown = MagicMock()
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[mock_col, mock_col])
        
        from src.ui.components.dynamic import Stepper
        
        stepper = Stepper("wizard", ["Step 1", "Step 2"])
        current = stepper.render()
        
        assert current == 0
        mock_st.progress.assert_called()
    
    @patch('src.ui.components.dynamic.st')
    def test_stepper_next(self, mock_st):
        """Test navigation suivant."""
        mock_st.session_state = {"wizard_step": 0}
        mock_st.rerun = MagicMock()
        
        from src.ui.components.dynamic import Stepper
        
        stepper = Stepper("wizard", ["S1", "S2", "S3"])
        stepper.next()
        
        assert mock_st.session_state["wizard_step"] == 1
    
    @patch('src.ui.components.dynamic.st')
    def test_stepper_previous(self, mock_st):
        """Test navigation prÃ©cÃ©dent."""
        mock_st.session_state = {"wizard_step": 2}
        mock_st.rerun = MagicMock()
        
        from src.ui.components.dynamic import Stepper
        
        stepper = Stepper("wizard", ["S1", "S2", "S3"])
        stepper.previous()
        
        assert mock_st.session_state["wizard_step"] == 1
    
    @patch('src.ui.components.dynamic.st')
    def test_stepper_reset(self, mock_st):
        """Test reset stepper."""
        mock_st.session_state = {"wizard_step": 2}
        
        from src.ui.components.dynamic import Stepper
        
        stepper = Stepper("wizard", ["S1", "S2", "S3"])
        stepper.reset()
        
        assert mock_st.session_state["wizard_step"] == 0
    
    @patch('src.ui.components.dynamic.st')
    def test_stepper_is_last_step(self, mock_st):
        """Test vÃ©rifier si derniÃ¨re Ã©tape."""
        mock_st.session_state = {"wizard_step": 2}
        
        from src.ui.components.dynamic import Stepper
        
        stepper = Stepper("wizard", ["S1", "S2", "S3"])
        
        assert stepper.is_last_step() is True


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS LAYOUT HEADER (header.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestLayoutHeader:
    """Tests pour header."""
    
    @patch('src.ui.layout.header.st')
    @patch('src.ui.layout.header.obtenir_parametres')
    @patch('src.ui.layout.header.obtenir_etat')
    @patch('src.ui.layout.header.badge')
    def test_afficher_header(self, mock_badge, mock_etat, mock_params, mock_st):
        """Test affichage header."""
        mock_params.return_value = MagicMock(APP_NAME="Test App")
        mock_etat.return_value = MagicMock(agent_ia=True, notifications_non_lues=0)
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[mock_col, mock_col, mock_col])
        mock_st.markdown = MagicMock()
        
        from src.ui.layout.header import afficher_header
        
        afficher_header()
        
        mock_st.markdown.assert_called()
        mock_badge.assert_called()
    
    @patch('src.ui.layout.header.st')
    @patch('src.ui.layout.header.obtenir_parametres')
    @patch('src.ui.layout.header.obtenir_etat')
    @patch('src.ui.layout.header.badge')
    def test_afficher_header_ia_indispo(self, mock_badge, mock_etat, mock_params, mock_st):
        """Test header avec IA indisponible."""
        mock_params.return_value = MagicMock(APP_NAME="Test")
        mock_etat.return_value = MagicMock(agent_ia=False, notifications_non_lues=0)
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[mock_col, mock_col, mock_col])
        mock_st.markdown = MagicMock()
        
        from src.ui.layout.header import afficher_header
        
        afficher_header()
        
        # Badge avec couleur warning pour IA indispo
        calls = mock_badge.call_args_list
        assert any("#FFC107" in str(c) for c in calls)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS LAYOUT FOOTER (footer.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestLayoutFooter:
    """Tests pour footer."""
    
    @patch('src.ui.layout.footer.st')
    @patch('src.ui.layout.footer.obtenir_parametres')
    def test_afficher_footer(self, mock_params, mock_st):
        """Test affichage footer."""
        mock_params.return_value = MagicMock(
            APP_NAME="Test App",
            APP_VERSION="1.0.0"
        )
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[mock_col, mock_col, mock_col])
        mock_st.markdown = MagicMock()
        mock_st.caption = MagicMock()
        mock_st.button = MagicMock(return_value=False)
        
        from src.ui.layout.footer import afficher_footer
        
        afficher_footer()
        
        mock_st.markdown.assert_called()
        mock_st.caption.assert_called()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS DATA TABLE (data.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestDataTable:
    """Tests pour data_table."""
    
    @patch('src.ui.components.data.st')
    def test_data_table_list(self, mock_st):
        """Test table depuis liste."""
        mock_st.dataframe = MagicMock()
        
        from src.ui.components.data import data_table
        
        data = [{"a": 1, "b": 2}]
        data_table(data)
        
        mock_st.dataframe.assert_called()
    
    @patch('src.ui.components.data.st')
    def test_data_table_dataframe(self, mock_st):
        """Test table depuis DataFrame."""
        import pandas as pd
        mock_st.dataframe = MagicMock()
        
        from src.ui.components.data import data_table
        
        df = pd.DataFrame({"a": [1], "b": [2]})
        data_table(df)
        
        mock_st.dataframe.assert_called()


class TestProgressBar:
    """Tests pour progress_bar."""
    
    @patch('src.ui.components.data.st')
    def test_progress_bar_basic(self, mock_st):
        """Test barre de progression."""
        mock_st.progress = MagicMock()
        mock_st.caption = MagicMock()
        
        from src.ui.components.data import progress_bar
        
        progress_bar(0.5)
        
        mock_st.progress.assert_called()
    
    @patch('src.ui.components.data.st')
    def test_progress_bar_with_label_param(self, mock_st):
        """Test avec label paramÃ¨tre."""
        mock_st.progress = MagicMock()
        
        from src.ui.components.data import progress_bar
        
        progress_bar(0.75, label="Chargement...")
        
        mock_st.progress.assert_called()


class TestStatusIndicator:
    """Tests pour status_indicator."""
    
    @patch('src.ui.components.data.st')
    def test_status_indicator_success(self, mock_st):
        """Test indicateur succÃ¨s."""
        mock_st.markdown = MagicMock()
        
        from src.ui.components.data import status_indicator
        
        status_indicator("success", "Actif")
        mock_st.markdown.assert_called()
    
    @patch('src.ui.components.data.st')
    def test_status_indicator_warning(self, mock_st):
        """Test indicateur warning."""
        mock_st.markdown = MagicMock()
        
        from src.ui.components.data import status_indicator
        
        status_indicator("warning", "En attente")
        mock_st.markdown.assert_called()
    
    @patch('src.ui.components.data.st')
    def test_status_indicator_error(self, mock_st):
        """Test indicateur erreur."""
        mock_st.markdown = MagicMock()
        
        from src.ui.components.data import status_indicator
        
        status_indicator("error", "Erreur")
        mock_st.markdown.assert_called()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS DASHBOARD WIDGETS ADDITIONNELS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGraphiqueProgressionObjectifs:
    """Tests pour graphique_progression_objectifs."""
    
    def test_graphique_objectifs_empty(self):
        """Test graphique vide."""
        from src.ui.components.dashboard_widgets import graphique_progression_objectifs
        
        result = graphique_progression_objectifs([])
        assert result is None
    
    def test_graphique_objectifs_with_data(self):
        """Test graphique avec donnÃ©es."""
        from src.ui.components.dashboard_widgets import graphique_progression_objectifs
        import plotly.graph_objects as go
        
        objectifs = [
            {"nom": "Sport", "progression": 75, "objectif": 100},
            {"nom": "Lecture", "progression": 50, "objectif": 100}
        ]
        
        result = graphique_progression_objectifs(objectifs)
        assert isinstance(result, go.Figure)


class TestIndicateurSanteSysteme:
    """Tests pour indicateur_sante_systeme."""
    
    def test_indicateur_sante_systeme(self):
        """Test indicateur santÃ©."""
        from src.ui.components.dashboard_widgets import indicateur_sante_systeme
        
        result = indicateur_sante_systeme()
        
        assert isinstance(result, dict)
        assert "global" in result
        assert "details" in result


class TestAfficherSanteSysteme:
    """Tests pour afficher_sante_systeme."""
    
    @patch('src.ui.components.dashboard_widgets.st')
    def test_afficher_sante_systeme(self, mock_st):
        """Test affichage santÃ© systÃ¨me."""
        mock_st.session_state = {}
        mock_expander = MagicMock()
        mock_expander.__enter__ = MagicMock(return_value=mock_expander)
        mock_expander.__exit__ = MagicMock(return_value=False)
        mock_st.expander = MagicMock(return_value=mock_expander)
        mock_st.markdown = MagicMock()
        
        from src.ui.components.dashboard_widgets import afficher_sante_systeme
        
        afficher_sante_systeme()
        
        mock_st.expander.assert_called()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS DOMAIN UI (domain.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestDomainUI:
    """Tests pour domain.py."""
    
    def test_import_domain_types(self):
        """Test import types UI."""
        from src.ui import domain
        
        # VÃ©rifier que le module existe
        assert hasattr(domain, '__file__')


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS QUICK FILTERS (forms.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestQuickFilters:
    """Tests pour quick_filters."""
    
    @patch('src.ui.components.forms.st')
    def test_quick_filters_basic(self, mock_st):
        """Test filtres rapides."""
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        # Fournir assez de colonnes pour les filtres
        mock_st.columns = MagicMock(return_value=[mock_col, mock_col, mock_col, mock_col])
        mock_st.button = MagicMock(return_value=False)
        mock_st.session_state = {}
        
        from src.ui.components.forms import quick_filters
        
        filters = {
            "status": ["Tous", "Actif", "Inactif"]
        }
        
        result = quick_filters(filters, "test")
        assert isinstance(result, dict)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CARD CONTAINER (layouts.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCardContainer:
    """Tests pour card_container."""
    
    @patch('src.ui.components.layouts.st')
    def test_card_container_basic(self, mock_st):
        """Test conteneur carte."""
        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=mock_container)
        mock_container.__exit__ = MagicMock(return_value=False)
        mock_st.container = MagicMock(return_value=mock_container)
        mock_st.markdown = MagicMock()
        
        from src.ui.components.layouts import card_container
        
        content_called = []
        def content_fn():
            content_called.append(True)
        
        card_container(content_fn)
        
        mock_st.markdown.assert_called()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS BASE_IO (base_io.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBaseIO:
    """Tests pour base_io.py."""
    
    def test_import_base_io(self):
        """Test import base_io."""
        from src.ui.core import base_io
        
        # Importer le module
        assert hasattr(base_io, '__file__')
