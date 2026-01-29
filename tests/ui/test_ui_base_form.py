"""
Tests pour src/ui/core/base_form.py
Générateur de formulaires universel
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit"""
    with patch("src.ui.core.base_form.st") as mock_st:
        # Mocks pour inputs
        mock_st.text_input.return_value = "test_value"
        mock_st.text_area.return_value = "textarea_value"
        mock_st.number_input.return_value = 42.0
        mock_st.selectbox.return_value = "option1"
        mock_st.multiselect.return_value = ["opt1", "opt2"]
        mock_st.checkbox.return_value = True
        mock_st.date_input.return_value = date(2026, 1, 28)
        mock_st.slider.return_value = 50

        # Mock form context manager
        mock_form = MagicMock()
        mock_form.__enter__ = MagicMock(return_value=None)
        mock_form.__exit__ = MagicMock(return_value=None)
        mock_st.form.return_value = mock_form

        # Mock columns
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=None)
        mock_col.__exit__ = MagicMock(return_value=None)
        mock_st.columns.return_value = [mock_col, mock_col]

        # Autres mocks
        mock_st.form_submit_button.return_value = False
        mock_st.markdown = MagicMock()
        mock_st.error = MagicMock()

        yield mock_st


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FORMBUILDER INITIALIZATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFormBuilderInit:
    """Tests pour l'initialisation de FormBuilder"""

    def test_init_basic(self):
        """Test initialisation basique"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test_form")

        assert form.form_id == "test_form"
        assert form.title is None
        assert form.fields == []
        assert form.data == {}

    def test_init_with_title(self):
        """Test initialisation avec titre"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test_form", title="Mon formulaire")

        assert form.title == "Mon formulaire"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ADD_TEXT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAddText:
    """Tests pour add_text()"""

    def test_add_text_basic(self):
        """Test ajout champ texte basique"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_text("nom", "Nom")

        assert len(form.fields) == 1
        assert form.fields[0]["type"] == "text"
        assert form.fields[0]["name"] == "nom"

    def test_add_text_required(self):
        """Test champ texte requis"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_text("nom", "Nom", required=True)

        assert " *" in form.fields[0]["label"]
        assert form.fields[0]["required"] is True

    def test_add_text_with_options(self):
        """Test champ texte avec options"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_text(
            "description",
            "Description",
            default="Défaut",
            max_length=100,
            help_text="Aide"
        )

        field = form.fields[0]
        assert field["default"] == "Défaut"
        assert field["max_length"] == 100
        assert field["help"] == "Aide"

    def test_add_text_chaining(self):
        """Test chaînage des méthodes"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        result = form.add_text("nom", "Nom")

        assert result is form  # Retourne self


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ADD_TEXTAREA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAddTextarea:
    """Tests pour add_textarea()"""

    def test_add_textarea_basic(self):
        """Test ajout textarea"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_textarea("description", "Description")

        assert form.fields[0]["type"] == "textarea"

    def test_add_textarea_with_height(self):
        """Test textarea avec hauteur"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_textarea("notes", "Notes", height=200)

        assert form.fields[0]["height"] == 200


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ADD_NUMBER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAddNumber:
    """Tests pour add_number()"""

    def test_add_number_basic(self):
        """Test ajout champ nombre"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_number("age", "Ã‚ge")

        assert form.fields[0]["type"] == "number"
        assert form.fields[0]["default"] == 0.0

    def test_add_number_with_range(self):
        """Test nombre avec min/max"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_number("age", "Ã‚ge", min_value=0, max_value=120)

        field = form.fields[0]
        assert field["min_value"] == 0
        assert field["max_value"] == 120

    def test_add_number_with_step(self):
        """Test nombre avec step"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_number("prix", "Prix", step=0.01)

        assert form.fields[0]["step"] == 0.01


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ADD_SELECT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAddSelect:
    """Tests pour add_select()"""

    def test_add_select_basic(self):
        """Test ajout select"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_select("categorie", "Catégorie", ["A", "B", "C"])

        assert form.fields[0]["type"] == "select"
        assert form.fields[0]["options"] == ["A", "B", "C"]

    def test_add_select_default_first_option(self):
        """Test valeur par défaut = première option"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_select("cat", "Cat", ["Premier", "Second"])

        assert form.fields[0]["default"] == "Premier"

    def test_add_select_custom_default(self):
        """Test valeur par défaut personnalisée"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_select("cat", "Cat", ["A", "B", "C"], default="B")

        assert form.fields[0]["default"] == "B"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ADD_MULTISELECT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAddMultiselect:
    """Tests pour add_multiselect()"""

    def test_add_multiselect_basic(self):
        """Test ajout multiselect"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_multiselect("tags", "Tags", ["A", "B", "C"])

        assert form.fields[0]["type"] == "multiselect"
        assert form.fields[0]["default"] == []

    def test_add_multiselect_with_default(self):
        """Test multiselect avec défaut"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_multiselect("tags", "Tags", ["A", "B", "C"], default=["A", "B"])

        assert form.fields[0]["default"] == ["A", "B"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ADD_CHECKBOX
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAddCheckbox:
    """Tests pour add_checkbox()"""

    def test_add_checkbox_basic(self):
        """Test ajout checkbox"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_checkbox("actif", "Actif")

        assert form.fields[0]["type"] == "checkbox"
        assert form.fields[0]["default"] is False

    def test_add_checkbox_default_true(self):
        """Test checkbox coché par défaut"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_checkbox("actif", "Actif", default=True)

        assert form.fields[0]["default"] is True


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ADD_DATE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAddDate:
    """Tests pour add_date()"""

    def test_add_date_basic(self):
        """Test ajout date"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_date("date_debut", "Date début")

        assert form.fields[0]["type"] == "date"
        assert form.fields[0]["default"] == date.today()

    def test_add_date_custom_default(self):
        """Test date avec défaut personnalisé"""
        from src.ui.core.base_form import FormBuilder

        custom_date = date(2026, 6, 15)
        form = FormBuilder("test")
        form.add_date("date_debut", "Date", default=custom_date)

        assert form.fields[0]["default"] == custom_date

    def test_add_date_with_range(self):
        """Test date avec min/max"""
        from src.ui.core.base_form import FormBuilder

        min_date = date(2020, 1, 1)
        max_date = date(2030, 12, 31)

        form = FormBuilder("test")
        form.add_date("date", "Date", min_value=min_date, max_value=max_date)

        field = form.fields[0]
        assert field["min_value"] == min_date
        assert field["max_value"] == max_date


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ADD_SLIDER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAddSlider:
    """Tests pour add_slider()"""

    def test_add_slider_basic(self):
        """Test ajout slider"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_slider("niveau", "Niveau")

        field = form.fields[0]
        assert field["type"] == "slider"
        assert field["min_value"] == 0
        assert field["max_value"] == 100
        assert field["default"] == 50

    def test_add_slider_custom_range(self):
        """Test slider avec range personnalisé"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_slider("temp", "Température", min_value=-10, max_value=40, default=20)

        field = form.fields[0]
        assert field["min_value"] == -10
        assert field["max_value"] == 40
        assert field["default"] == 20


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ADD_DIVIDER / ADD_HEADER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAddDividerHeader:
    """Tests pour add_divider() et add_header()"""

    def test_add_divider(self):
        """Test ajout séparateur"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_divider()

        assert form.fields[0]["type"] == "divider"

    def test_add_header(self):
        """Test ajout header"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_header("Section 1")

        assert form.fields[0]["type"] == "header"
        assert form.fields[0]["text"] == "Section 1"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS RENDER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRender:
    """Tests pour render()"""

    def test_render_basic(self, mock_streamlit):
        """Test render basique"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_text("nom", "Nom")

        result = form.render()

        mock_streamlit.form.assert_called_once_with("test")
        assert result is False  # Pas soumis

    def test_render_with_title(self, mock_streamlit):
        """Test render avec titre"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test", title="Mon Form")
        form.render()

        mock_streamlit.markdown.assert_any_call("### Mon Form")

    def test_render_submit_success(self, mock_streamlit):
        """Test soumission réussie"""
        from src.ui.core.base_form import FormBuilder

        mock_streamlit.form_submit_button.side_effect = [True, False]  # Submit True, Cancel False

        form = FormBuilder("test")
        form.add_text("nom", "Nom")

        on_submit = MagicMock()
        result = form.render(on_submit=on_submit)

        assert result is True
        on_submit.assert_called_once()

    def test_render_cancel(self, mock_streamlit):
        """Test annulation"""
        from src.ui.core.base_form import FormBuilder

        mock_streamlit.form_submit_button.side_effect = [False, True]  # Submit False, Cancel True

        form = FormBuilder("test")

        on_cancel = MagicMock()
        result = form.render(on_cancel=on_cancel)

        assert result is False
        on_cancel.assert_called_once()

    def test_render_validation_error(self, mock_streamlit):
        """Test erreur de validation"""
        from src.ui.core.base_form import FormBuilder

        mock_streamlit.form_submit_button.side_effect = [True, False]
        mock_streamlit.text_input.return_value = ""  # Champ vide

        form = FormBuilder("test")
        form.add_text("nom", "Nom", required=True)

        result = form.render()

        assert result is False
        mock_streamlit.error.assert_called()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS _RENDER_FIELD
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRenderField:
    """Tests pour _render_field()"""

    def test_render_text_field(self, mock_streamlit):
        """Test rendu champ texte"""
        from src.ui.core.base_form import FormBuilder

        mock_streamlit.form_submit_button.return_value = False

        form = FormBuilder("test")
        form.add_text("nom", "Nom", default="Test")
        form.render()

        mock_streamlit.text_input.assert_called()

    def test_render_number_field(self, mock_streamlit):
        """Test rendu champ nombre"""
        from src.ui.core.base_form import FormBuilder

        mock_streamlit.form_submit_button.return_value = False

        form = FormBuilder("test")
        form.add_number("age", "Ã‚ge")
        form.render()

        mock_streamlit.number_input.assert_called()

    def test_render_divider(self, mock_streamlit):
        """Test rendu séparateur"""
        from src.ui.core.base_form import FormBuilder

        mock_streamlit.form_submit_button.return_value = False

        form = FormBuilder("test")
        form.add_divider()
        form.render()

        mock_streamlit.markdown.assert_any_call("---")

    def test_render_header(self, mock_streamlit):
        """Test rendu header"""
        from src.ui.core.base_form import FormBuilder

        mock_streamlit.form_submit_button.return_value = False

        form = FormBuilder("test")
        form.add_header("Section")
        form.render()

        mock_streamlit.markdown.assert_any_call("#### Section")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS _VALIDATE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestValidate:
    """Tests pour _validate()"""

    def test_validate_no_required_fields(self):
        """Test validation sans champs requis"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_text("nom", "Nom")
        form.data = {"nom": ""}

        assert form._validate() is True

    def test_validate_required_field_empty(self):
        """Test validation champ requis vide"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_text("nom", "Nom", required=True)
        form.data = {"nom": ""}

        assert form._validate() is False

    def test_validate_required_field_filled(self):
        """Test validation champ requis rempli"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_text("nom", "Nom", required=True)
        form.data = {"nom": "Test"}

        assert form._validate() is True

    def test_validate_required_list_empty(self):
        """Test validation liste requise vide"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_multiselect("tags", "Tags", ["A", "B"], required=True)
        form.data = {"tags": []}

        assert form._validate() is False

    def test_validate_required_list_filled(self):
        """Test validation liste requise remplie"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.add_multiselect("tags", "Tags", ["A", "B"], required=True)
        form.data = {"tags": ["A"]}

        assert form._validate() is True


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GET_DATA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGetData:
    """Tests pour get_data()"""

    def test_get_data_empty(self):
        """Test données vides"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")

        assert form.get_data() == {}

    def test_get_data_with_values(self):
        """Test données avec valeurs"""
        from src.ui.core.base_form import FormBuilder

        form = FormBuilder("test")
        form.data = {"nom": "Test", "age": 25}

        data = form.get_data()

        assert data["nom"] == "Test"
        assert data["age"] == 25

