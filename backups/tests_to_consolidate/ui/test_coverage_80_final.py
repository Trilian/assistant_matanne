"""
Tests étendus pour couverture UI 80%+ - Partie 3

Couvre:
- FormBuilder render et validation (base_form.py)  
- BaseIOService (base_io.py)
- Sidebar menu helpers (sidebar.py)
- initialiser_app (init.py)
- domain.py
- camera_scanner basique
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import date
import pandas as pd


# ═══════════════════════════════════════════════════════════
# TESTS FORM BUILDER RENDER (base_form.py)
# ═══════════════════════════════════════════════════════════


class TestFormBuilderRender:
    """Tests pour FormBuilder._render_field."""
    
    @patch('src.ui.core.base_form.st')
    def test_render_field_text(self, mock_st):
        """Test render champ texte."""
        mock_st.text_input = MagicMock(return_value="valeur test")
        
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        field = {
            "type": "text",
            "name": "nom",
            "label": "Nom",
            "default": "",
            "max_length": None,
            "help": None
        }
        form._render_field(field)
        
        assert form.data["nom"] == "valeur test"
    
    @patch('src.ui.core.base_form.st')
    def test_render_field_textarea(self, mock_st):
        """Test render textarea."""
        mock_st.text_area = MagicMock(return_value="texte long")
        
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        field = {
            "type": "textarea",
            "name": "desc",
            "label": "Description",
            "default": "",
            "height": 100,
            "help": None
        }
        form._render_field(field)
        
        assert form.data["desc"] == "texte long"
    
    @patch('src.ui.core.base_form.st')
    def test_render_field_number(self, mock_st):
        """Test render number."""
        mock_st.number_input = MagicMock(return_value=42.0)
        
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        field = {
            "type": "number",
            "name": "qty",
            "label": "Quantité",
            "default": 0,
            "min_value": None,
            "max_value": None,
            "step": 1.0,
            "help": None
        }
        form._render_field(field)
        
        assert form.data["qty"] == 42.0
    
    @patch('src.ui.core.base_form.st')
    def test_render_field_select(self, mock_st):
        """Test render select."""
        mock_st.selectbox = MagicMock(return_value="Option 2")
        
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        field = {
            "type": "select",
            "name": "cat",
            "label": "Catégorie",
            "options": ["Option 1", "Option 2", "Option 3"],
            "default": "Option 1",
            "help": None
        }
        form._render_field(field)
        
        assert form.data["cat"] == "Option 2"
    
    @patch('src.ui.core.base_form.st')
    def test_render_field_multiselect(self, mock_st):
        """Test render multiselect."""
        mock_st.multiselect = MagicMock(return_value=["A", "C"])
        
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        field = {
            "type": "multiselect",
            "name": "tags",
            "label": "Tags",
            "options": ["A", "B", "C"],
            "default": [],
            "help": None
        }
        form._render_field(field)
        
        assert form.data["tags"] == ["A", "C"]
    
    @patch('src.ui.core.base_form.st')
    def test_render_field_checkbox(self, mock_st):
        """Test render checkbox."""
        mock_st.checkbox = MagicMock(return_value=True)
        
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        field = {
            "type": "checkbox",
            "name": "active",
            "label": "Actif",
            "default": False,
            "help": None
        }
        form._render_field(field)
        
        assert form.data["active"] is True
    
    @patch('src.ui.core.base_form.st')
    def test_render_field_date(self, mock_st):
        """Test render date."""
        today = date.today()
        mock_st.date_input = MagicMock(return_value=today)
        
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        field = {
            "type": "date",
            "name": "date",
            "label": "Date",
            "default": today,
            "min_value": None,
            "max_value": None,
            "help": None
        }
        form._render_field(field)
        
        assert form.data["date"] == today
    
    @patch('src.ui.core.base_form.st')
    def test_render_field_slider(self, mock_st):
        """Test render slider."""
        mock_st.slider = MagicMock(return_value=75)
        
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        field = {
            "type": "slider",
            "name": "rating",
            "label": "Note",
            "min_value": 0,
            "max_value": 100,
            "default": 50,
            "help": None
        }
        form._render_field(field)
        
        assert form.data["rating"] == 75
    
    @patch('src.ui.core.base_form.st')
    def test_render_field_divider(self, mock_st):
        """Test render divider."""
        mock_st.markdown = MagicMock()
        
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form._render_field({"type": "divider"})
        
        mock_st.markdown.assert_called_with("---")
    
    @patch('src.ui.core.base_form.st')
    def test_render_field_header(self, mock_st):
        """Test render header."""
        mock_st.markdown = MagicMock()
        
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form._render_field({"type": "header", "text": "Section 1"})
        
        mock_st.markdown.assert_called_with("#### Section 1")


class TestFormBuilderValidation:
    """Tests pour FormBuilder._validate."""
    
    def test_validate_success(self):
        """Test validation réussie."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.fields = [
            {"name": "nom", "required": True},
            {"name": "opt", "required": False}
        ]
        form.data = {"nom": "Test", "opt": ""}
        
        assert form._validate() is True
    
    def test_validate_fail_empty_string(self):
        """Test validation échoue avec chaîne vide."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.fields = [{"name": "nom", "required": True}]
        form.data = {"nom": ""}
        
        assert form._validate() is False
    
    def test_validate_fail_none(self):
        """Test validation échoue avec None."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.fields = [{"name": "nom", "required": True}]
        form.data = {"nom": None}
        
        assert form._validate() is False
    
    def test_validate_fail_empty_list(self):
        """Test validation échoue avec liste vide."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.fields = [{"name": "tags", "required": True}]
        form.data = {"tags": []}
        
        assert form._validate() is False
    
    def test_get_data(self):
        """Test récupération données."""
        from src.ui.core.base_form import FormBuilder
        
        form = FormBuilder("test")
        form.data = {"nom": "Test", "qty": 5}
        
        data = form.get_data()
        assert data == {"nom": "Test", "qty": 5}


# ═══════════════════════════════════════════════════════════
# TESTS BASE IO SERVICE (base_io.py)
# ═══════════════════════════════════════════════════════════


class TestIOConfig:
    """Tests pour IOConfig."""
    
    def test_io_config_init(self):
        """Test création config IO."""
        from src.ui.core.base_io import IOConfig
        
        config = IOConfig(
            field_mapping={"nom": "Nom", "qty": "Quantité"},
            required_fields=["nom"]
        )
        
        assert config.field_mapping["nom"] == "Nom"
        assert "nom" in config.required_fields
    
    def test_io_config_with_transformers(self):
        """Test config avec transformers."""
        from src.ui.core.base_io import IOConfig
        
        config = IOConfig(
            field_mapping={"nom": "Nom"},
            required_fields=["nom"],
            transformers={"nom": str.upper}
        )
        
        assert config.transformers is not None
        assert config.transformers["nom"]("test") == "TEST"


class TestBaseIOService:
    """Tests pour BaseIOService."""
    
    def test_base_io_service_init(self):
        """Test init BaseIOService."""
        from src.ui.core.base_io import IOConfig, BaseIOService
        
        config = IOConfig(
            field_mapping={"nom": "Nom"},
            required_fields=["nom"]
        )
        
        io = BaseIOService(config)
        assert io.config == config


# ═══════════════════════════════════════════════════════════
# TESTS INITIALISER APP (init.py)
# ═══════════════════════════════════════════════════════════


class TestInitialiserApp:
    """Tests pour initialiser_app."""
    
    @patch('src.ui.layout.init.verifier_connexion')
    @patch('src.ui.layout.init.GestionnaireEtat')
    @patch('src.ui.layout.init.obtenir_etat')
    @patch('src.ui.layout.init.st')
    def test_initialiser_app_success(self, mock_st, mock_get_etat, mock_gest, mock_db):
        """Test init réussie."""
        mock_db.return_value = True
        mock_get_etat.return_value = MagicMock(agent_ia=True)
        
        from src.ui.layout.init import initialiser_app
        
        result = initialiser_app()
        
        assert result is True
        mock_gest.initialiser.assert_called_once()
    
    @patch('src.ui.layout.init.verifier_connexion')
    @patch('src.ui.layout.init.GestionnaireEtat')
    @patch('src.ui.layout.init.st')
    def test_initialiser_app_db_fail(self, mock_st, mock_gest, mock_db):
        """Test init échoue si DB indisponible."""
        mock_db.return_value = False
        mock_st.error = MagicMock()
        mock_st.stop = MagicMock(side_effect=SystemExit)
        
        from src.ui.layout.init import initialiser_app
        
        with pytest.raises(SystemExit):
            initialiser_app()
        
        mock_st.error.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS SIDEBAR (sidebar.py)
# ═══════════════════════════════════════════════════════════


class TestSidebar:
    """Tests pour afficher_sidebar."""
    
    @patch('src.ui.layout.sidebar.afficher_stats_chargement_differe')
    @patch('src.ui.layout.sidebar.GestionnaireEtat')
    @patch('src.ui.layout.sidebar.obtenir_etat')
    @patch('src.ui.layout.sidebar.st')
    def test_afficher_sidebar(self, mock_st, mock_get_etat, mock_gest, mock_stats):
        """Test affichage sidebar."""
        mock_sidebar = MagicMock()
        mock_sidebar.__enter__ = MagicMock(return_value=mock_sidebar)
        mock_sidebar.__exit__ = MagicMock(return_value=False)
        mock_st.sidebar = mock_sidebar
        
        mock_get_etat.return_value = MagicMock(
            module_actuel="accueil",
            mode_debug=False
        )
        mock_gest.obtenir_fil_ariane_navigation.return_value = ["Accueil"]
        
        from src.ui.layout.sidebar import afficher_sidebar
        
        afficher_sidebar()
        
        mock_st.sidebar.__enter__.assert_called()


class TestRendreMenu:
    """Tests pour _rendre_menu."""
    
    @patch('src.ui.layout.sidebar.st')
    def test_rendre_menu_simple(self, mock_st):
        """Test rendu menu simple."""
        mock_st.button = MagicMock(return_value=False)
        
        from src.ui.layout.sidebar import _rendre_menu
        
        menu = {"🏠 Accueil": "accueil"}
        etat = MagicMock(module_actuel="accueil")
        
        _rendre_menu(menu, etat)
        
        mock_st.button.assert_called()
    
    @patch('src.ui.layout.sidebar.st')
    def test_rendre_menu_nested(self, mock_st):
        """Test rendu menu avec sous-menus."""
        mock_expander = MagicMock()
        mock_expander.__enter__ = MagicMock(return_value=mock_expander)
        mock_expander.__exit__ = MagicMock(return_value=False)
        mock_st.expander = MagicMock(return_value=mock_expander)
        mock_st.button = MagicMock(return_value=False)
        mock_st.divider = MagicMock()
        
        from src.ui.layout.sidebar import _rendre_menu
        
        menu = {
            "🍳 Cuisine": {
                "🍽️ Recettes": "cuisine.recettes",
                "───────────": None,  # Séparateur
                "🛒 Courses": "cuisine.courses"
            }
        }
        etat = MagicMock(module_actuel="cuisine.recettes")
        
        _rendre_menu(menu, etat)
        
        mock_st.expander.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS CAMERA SCANNER (camera_scanner.py)
# ═══════════════════════════════════════════════════════════


class TestCameraScannerDetection:
    """Tests pour fonctions de détection."""
    
    def test_detect_barcode_pyzbar_not_installed(self):
        """Test détection sans pyzbar."""
        from src.ui.components.camera_scanner import _detect_barcode_pyzbar
        
        # Crée un faux frame numpy
        import numpy as np
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Devrait retourner liste vide si pyzbar pas installé
        result = _detect_barcode_pyzbar(frame)
        assert isinstance(result, list)
    
    def test_detect_barcode_zxing_not_installed(self):
        """Test détection sans zxing."""
        from src.ui.components.camera_scanner import _detect_barcode_zxing
        
        import numpy as np
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = _detect_barcode_zxing(frame)
        assert isinstance(result, list)
    
    def test_detect_barcodes(self):
        """Test détection barcodes (wrapper)."""
        from src.ui.components.camera_scanner import detect_barcodes
        
        import numpy as np
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = detect_barcodes(frame)
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════
# TESTS DOMAIN UI (domain.py)
# ═══════════════════════════════════════════════════════════


class TestDomainUITypes:
    """Tests pour types domain.py."""
    
    def test_import_domain(self):
        """Test import domain module."""
        from src.ui import domain
        
        # Module doit exister
        assert domain is not None


# ═══════════════════════════════════════════════════════════
# TESTS ATOMS ADDITIONNELS (atoms.py)
# ═══════════════════════════════════════════════════════════


class TestAtomsToast:
    """Tests pour toast."""
    
    @patch('src.ui.components.atoms.st')
    def test_toast_success(self, mock_st):
        """Test toast success."""
        mock_st.success = MagicMock()
        
        from src.ui.components.atoms import toast
        
        toast("Message", "success")
        mock_st.success.assert_called_with("Message")
    
    @patch('src.ui.components.atoms.st')
    def test_toast_error(self, mock_st):
        """Test toast error."""
        mock_st.error = MagicMock()
        
        from src.ui.components.atoms import toast
        
        toast("Erreur", "error")
        mock_st.error.assert_called_with("Erreur")
    
    @patch('src.ui.components.atoms.st')
    def test_toast_warning(self, mock_st):
        """Test toast warning."""
        mock_st.warning = MagicMock()
        
        from src.ui.components.atoms import toast
        
        toast("Attention", "warning")
        mock_st.warning.assert_called_with("Attention")
    
    @patch('src.ui.components.atoms.st')
    def test_toast_info(self, mock_st):
        """Test toast info."""
        mock_st.info = MagicMock()
        
        from src.ui.components.atoms import toast
        
        toast("Info", "info")
        mock_st.info.assert_called_with("Info")


class TestAtomsDivider:
    """Tests pour divider."""
    
    @patch('src.ui.components.atoms.st')
    def test_divider_simple(self, mock_st):
        """Test divider sans texte."""
        mock_st.markdown = MagicMock()
        
        from src.ui.components.atoms import divider
        
        divider()
        mock_st.markdown.assert_called_with("---")
    
    @patch('src.ui.components.atoms.st')
    def test_divider_with_text(self, mock_st):
        """Test divider avec texte."""
        mock_st.markdown = MagicMock()
        
        from src.ui.components.atoms import divider
        
        divider("OU")
        
        # Vérifier que markdown est appelé avec le texte
        call_args = mock_st.markdown.call_args[0][0]
        assert "OU" in call_args


class TestAtomsInfoBox:
    """Tests pour info_box."""
    
    @patch('src.ui.components.atoms.st')
    def test_info_box(self, mock_st):
        """Test info box."""
        mock_st.markdown = MagicMock()
        
        from src.ui.components.atoms import info_box
        
        info_box("Titre", "Contenu", "💡")
        
        call_args = mock_st.markdown.call_args[0][0]
        assert "Titre" in call_args
        assert "Contenu" in call_args


# ═══════════════════════════════════════════════════════════
# TESTS DYNAMIC LIST RENDER (dynamic.py)
# ═══════════════════════════════════════════════════════════


class TestDynamicListRender:
    """Tests pour DynamicList.render."""
    
    @patch('src.ui.components.dynamic.form_field')
    @patch('src.ui.components.dynamic.st')
    def test_dynamic_list_render_empty(self, mock_st, mock_form_field):
        """Test render liste vide."""
        mock_st.session_state = {"test_items": []}
        mock_expander = MagicMock()
        mock_expander.__enter__ = MagicMock(return_value=mock_expander)
        mock_expander.__exit__ = MagicMock(return_value=False)
        mock_st.expander = MagicMock(return_value=mock_expander)
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[mock_col, mock_col])
        mock_st.button = MagicMock(return_value=False)
        mock_st.info = MagicMock()
        mock_form_field.return_value = "value"
        
        from src.ui.components.dynamic import DynamicList
        
        fields = [{"name": "nom", "type": "text", "label": "Nom"}]
        dl = DynamicList("test", fields)
        
        items = dl.render()
        
        assert items == []
        mock_st.info.assert_called()


class TestStepperEdgeCases:
    """Tests cas limites Stepper."""
    
    @patch('src.ui.components.dynamic.st')
    def test_stepper_next_at_last(self, mock_st):
        """Test next à la dernière étape."""
        mock_st.session_state = {"wizard_step": 2}
        mock_st.rerun = MagicMock()
        
        from src.ui.components.dynamic import Stepper
        
        stepper = Stepper("wizard", ["S1", "S2", "S3"])
        stepper.next()
        
        # Ne doit pas dépasser le max
        assert mock_st.session_state["wizard_step"] == 2
        mock_st.rerun.assert_not_called()
    
    @patch('src.ui.components.dynamic.st')
    def test_stepper_previous_at_first(self, mock_st):
        """Test previous à la première étape."""
        mock_st.session_state = {"wizard_step": 0}
        mock_st.rerun = MagicMock()
        
        from src.ui.components.dynamic import Stepper
        
        stepper = Stepper("wizard", ["S1", "S2", "S3"])
        stepper.previous()
        
        # Ne doit pas aller en négatif
        assert mock_st.session_state["wizard_step"] == 0
        mock_st.rerun.assert_not_called()
    
    @patch('src.ui.components.dynamic.st')
    def test_stepper_is_last_step_false(self, mock_st):
        """Test is_last_step quand pas à la fin."""
        mock_st.session_state = {"wizard_step": 0}
        
        from src.ui.components.dynamic import Stepper
        
        stepper = Stepper("wizard", ["S1", "S2", "S3"])
        
        assert stepper.is_last_step() is False


# ═══════════════════════════════════════════════════════════
# TESTS DATA ADDITIONNELS (data.py)
# ═══════════════════════════════════════════════════════════


class TestDataTableEdgeCases:
    """Tests cas limites data_table."""
    
    @patch('src.ui.components.data.st')
    def test_data_table_empty_list(self, mock_st):
        """Test table avec liste vide."""
        mock_st.dataframe = MagicMock()
        
        from src.ui.components.data import data_table
        
        data_table([])
        mock_st.dataframe.assert_called()


class TestExportButtonsFormats:
    """Tests formats export_buttons."""
    
    @patch('src.ui.components.data.st')
    def test_export_buttons_json_only(self, mock_st):
        """Test export JSON uniquement."""
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[mock_col])
        mock_st.download_button = MagicMock(return_value=False)
        
        from src.ui.components.data import export_buttons
        
        data = [{"a": 1}]
        export_buttons(data, "test", formats=["json"])
        
        # Vérifier appel download_button avec JSON
        assert mock_st.download_button.called


# ═══════════════════════════════════════════════════════════
# TESTS LAYOUTS ADDITIONNELS (layouts.py)
# ═══════════════════════════════════════════════════════════


class TestTabsLayoutContent:
    """Tests contenu tabs_layout."""
    
    @patch('src.ui.components.layouts.st')
    def test_tabs_layout_calls_content(self, mock_st):
        """Test que tabs_layout appelle le contenu."""
        mock_tab = MagicMock()
        mock_tab.__enter__ = MagicMock(return_value=mock_tab)
        mock_tab.__exit__ = MagicMock(return_value=False)
        mock_st.tabs = MagicMock(return_value=[mock_tab])
        
        from src.ui.components.layouts import tabs_layout
        
        content_called = []
        tab_data = {
            "Tab 1": lambda: content_called.append(1)
        }
        
        tabs_layout(tab_data)
        
        # Contenu devrait être appelé
        assert 1 in content_called


class TestCardContainerColor:
    """Tests card_container avec couleur."""
    
    @patch('src.ui.components.layouts.st')
    def test_card_container_custom_color(self, mock_st):
        """Test carte avec couleur personnalisée."""
        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=mock_container)
        mock_container.__exit__ = MagicMock(return_value=False)
        mock_st.container = MagicMock(return_value=mock_container)
        mock_st.markdown = MagicMock()
        
        from src.ui.components.layouts import card_container
        
        card_container(lambda: None, color="#FFCCCC")
        
        # Vérifier que markdown est appelé avec la couleur
        calls = mock_st.markdown.call_args_list
        assert any("#FFCCCC" in str(c) for c in calls)
