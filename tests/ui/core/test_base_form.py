"""
Tests complets pour src/ui/core/base_form.py
Couverture cible: >80%
"""

from datetime import date
from unittest.mock import MagicMock, patch

# ═══════════════════════════════════════════════════════════
# CONSTRUCTEUR FORMULAIRE - CRÉATION
# ═══════════════════════════════════════════════════════════


class TestConstructeurFormulaireCreation:
    """Tests pour création ConstructeurFormulaire."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.core.base_form import ConstructeurFormulaire

        assert ConstructeurFormulaire is not None

    def test_creation_simple(self):
        """Test création basique."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test_form")

        assert form.form_id == "test_form"
        assert form.title is None
        assert form.fields == []
        assert form.data == {}

    def test_creation_with_title(self):
        """Test création avec titre."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("my_form", title="Mon Formulaire")

        assert form.form_id == "my_form"
        assert form.title == "Mon Formulaire"

    def test_alias_form_builder(self):
        """Test alias FormBuilder."""
        from src.ui.core.base_form import ConstructeurFormulaire, FormBuilder

        assert FormBuilder is ConstructeurFormulaire


# ═══════════════════════════════════════════════════════════
# AJOUT CHAMPS
# ═══════════════════════════════════════════════════════════


class TestAjoutChamps:
    """Tests pour les méthodes add_*."""

    def test_add_text(self):
        """Test add_text."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        result = form.add_text("nom", "Nom", required=True, default="Test")

        assert result is form  # Chaînage
        assert len(form.fields) == 1
        assert form.fields[0]["type"] == "text"
        assert form.fields[0]["name"] == "nom"
        assert form.fields[0]["label"] == "Nom *"  # * pour required
        assert form.fields[0]["default"] == "Test"

    def test_add_text_with_max_length(self):
        """Test add_text avec max_length."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form.add_text("code", "Code", max_length=10, help_text="Max 10 chars")

        assert form.fields[0]["max_length"] == 10
        assert form.fields[0]["help"] == "Max 10 chars"

    def test_add_textarea(self):
        """Test add_textarea."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form.add_textarea("desc", "Description", required=False, height=200)

        assert form.fields[0]["type"] == "textarea"
        assert form.fields[0]["height"] == 200
        assert form.fields[0]["label"] == "Description"  # Pas de * car required=False

    def test_add_number(self):
        """Test add_number."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form.add_number("qty", "Quantité", min_value=0, max_value=100, step=1.0, default=10)

        assert form.fields[0]["type"] == "number"
        assert form.fields[0]["min_value"] == 0
        assert form.fields[0]["max_value"] == 100
        assert form.fields[0]["step"] == 1.0
        assert form.fields[0]["default"] == 10

    def test_add_select(self):
        """Test add_select."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form.add_select("type", "Type", options=["A", "B", "C"], default="B")

        assert form.fields[0]["type"] == "select"
        assert form.fields[0]["options"] == ["A", "B", "C"]
        assert form.fields[0]["default"] == "B"

    def test_add_select_default_first(self):
        """Test add_select default to first option."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form.add_select("type", "Type", options=["X", "Y"], default=None)

        assert form.fields[0]["default"] == "X"  # First option

    def test_add_multiselect(self):
        """Test add_multiselect."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form.add_multiselect("tags", "Tags", options=["A", "B", "C"], default=["A", "B"])

        assert form.fields[0]["type"] == "multiselect"
        assert form.fields[0]["default"] == ["A", "B"]

    def test_add_multiselect_empty_default(self):
        """Test add_multiselect sans default."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form.add_multiselect("tags", "Tags", options=["A", "B"])

        assert form.fields[0]["default"] == []

    def test_add_checkbox(self):
        """Test add_checkbox."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form.add_checkbox("active", "Actif", default=True)

        assert form.fields[0]["type"] == "checkbox"
        assert form.fields[0]["default"] is True

    def test_add_date(self):
        """Test add_date."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        test_date = date(2025, 1, 15)
        form.add_date("date", "Date", default=test_date, min_value=date(2020, 1, 1))

        assert form.fields[0]["type"] == "date"
        assert form.fields[0]["default"] == test_date
        assert form.fields[0]["min_value"] == date(2020, 1, 1)

    def test_add_date_default_today(self):
        """Test add_date default to today."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form.add_date("date", "Date")

        assert form.fields[0]["default"] == date.today()

    def test_add_slider(self):
        """Test add_slider."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form.add_slider("rating", "Note", min_value=1, max_value=5, default=3)

        assert form.fields[0]["type"] == "slider"
        assert form.fields[0]["min_value"] == 1
        assert form.fields[0]["max_value"] == 5
        assert form.fields[0]["default"] == 3

    def test_add_divider(self):
        """Test add_divider."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        result = form.add_divider()

        assert result is form
        assert form.fields[0]["type"] == "divider"

    def test_add_header(self):
        """Test add_header."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        result = form.add_header("Section")

        assert result is form
        assert form.fields[0]["type"] == "header"
        assert form.fields[0]["text"] == "Section"

    def test_chaining(self):
        """Test chaînage des méthodes."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = (
            ConstructeurFormulaire("test")
            .add_text("nom", "Nom")
            .add_number("age", "Ã‚ge")
            .add_divider()
            .add_checkbox("ok", "OK")
        )

        assert len(form.fields) == 4


# ═══════════════════════════════════════════════════════════
# RENDER CHAMPS
# ═══════════════════════════════════════════════════════════


class TestRenderChamps:
    """Tests pour _render_field."""

    @patch("streamlit.markdown")
    def test_render_divider(self, mock_md):
        """Test render divider."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form._render_field({"type": "divider"})

        mock_md.assert_called_with("---")

    @patch("streamlit.markdown")
    def test_render_header(self, mock_md):
        """Test render header."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form._render_field({"type": "header", "text": "Section"})

        mock_md.assert_called_with("#### Section")

    @patch("streamlit.text_input", return_value="texte saisi")
    def test_render_text(self, mock_input):
        """Test render text."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form._render_field(
            {
                "type": "text",
                "name": "nom",
                "label": "Nom",
                "default": "",
                "max_length": None,
                "help": None,
            }
        )

        mock_input.assert_called_once()
        assert form.data["nom"] == "texte saisi"

    @patch("streamlit.text_area", return_value="long texte")
    def test_render_textarea(self, mock_area):
        """Test render textarea."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form._render_field(
            {
                "type": "textarea",
                "name": "desc",
                "label": "Description",
                "default": "",
                "height": 100,
                "help": None,
            }
        )

        mock_area.assert_called_once()
        assert form.data["desc"] == "long texte"

    @patch("streamlit.number_input", return_value=42.0)
    def test_render_number(self, mock_num):
        """Test render number."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form._render_field(
            {
                "type": "number",
                "name": "qty",
                "label": "Quantité",
                "default": 0,
                "min_value": None,
                "max_value": None,
                "step": 1.0,
                "help": None,
            }
        )

        assert form.data["qty"] == 42.0

    @patch("streamlit.selectbox", return_value="B")
    def test_render_select(self, mock_sel):
        """Test render select."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form._render_field(
            {
                "type": "select",
                "name": "type",
                "label": "Type",
                "options": ["A", "B", "C"],
                "default": "A",
                "help": None,
            }
        )

        assert form.data["type"] == "B"

    @patch("streamlit.multiselect", return_value=["X", "Y"])
    def test_render_multiselect(self, mock_multi):
        """Test render multiselect."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form._render_field(
            {
                "type": "multiselect",
                "name": "tags",
                "label": "Tags",
                "options": ["X", "Y", "Z"],
                "default": [],
                "help": None,
            }
        )

        assert form.data["tags"] == ["X", "Y"]

    @patch("streamlit.checkbox", return_value=True)
    def test_render_checkbox(self, mock_check):
        """Test render checkbox."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form._render_field(
            {"type": "checkbox", "name": "active", "label": "Actif", "default": False, "help": None}
        )

        assert form.data["active"] is True

    @patch("streamlit.date_input", return_value=date(2025, 6, 15))
    def test_render_date(self, mock_date):
        """Test render date."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form._render_field(
            {
                "type": "date",
                "name": "date",
                "label": "Date",
                "default": date.today(),
                "min_value": None,
                "max_value": None,
                "help": None,
            }
        )

        assert form.data["date"] == date(2025, 6, 15)

    @patch("streamlit.slider", return_value=75)
    def test_render_slider(self, mock_slider):
        """Test render slider."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form._render_field(
            {
                "type": "slider",
                "name": "rating",
                "label": "Note",
                "min_value": 0,
                "max_value": 100,
                "default": 50,
                "help": None,
            }
        )

        assert form.data["rating"] == 75


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


class TestValidation:
    """Tests pour _validate."""

    def test_validate_valid_data(self):
        """Test validation avec données valides."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form.fields = [{"name": "nom", "required": True}]
        form.data = {"nom": "Test"}

        assert form._validate() is True

    def test_validate_missing_required(self):
        """Test validation avec champ requis manquant."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form.fields = [{"name": "nom", "required": True}]
        form.data = {"nom": ""}

        assert form._validate() is False

    def test_validate_missing_required_none(self):
        """Test validation avec champ requis None."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form.fields = [{"name": "nom", "required": True}]
        form.data = {"nom": None}

        assert form._validate() is False

    def test_validate_missing_required_empty_list(self):
        """Test validation avec liste vide."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form.fields = [{"name": "tags", "required": True}]
        form.data = {"tags": []}

        assert form._validate() is False

    def test_validate_optional_field(self):
        """Test validation champ optionnel."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form.fields = [{"name": "nom", "required": False}]
        form.data = {"nom": ""}

        assert form._validate() is True

    def test_get_data(self):
        """Test get_data."""
        from src.ui.core.base_form import ConstructeurFormulaire

        form = ConstructeurFormulaire("test")
        form.data = {"nom": "Test", "age": 25}

        assert form.get_data() == {"nom": "Test", "age": 25}


# ═══════════════════════════════════════════════════════════
# RENDER FORMULAIRE COMPLET
# ═══════════════════════════════════════════════════════════


class TestRenderFormulaire:
    """Tests pour render."""

    @patch("streamlit.markdown")
    @patch("streamlit.form")
    @patch("streamlit.columns")
    @patch("streamlit.form_submit_button")
    def test_render_with_title(self, mock_submit, mock_cols, mock_form, mock_md):
        """Test render avec titre."""
        from src.ui.core.base_form import ConstructeurFormulaire

        mock_form.return_value.__enter__ = MagicMock()
        mock_form.return_value.__exit__ = MagicMock()

        mock_cols.return_value = [MagicMock(), MagicMock()]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        mock_submit.side_effect = [False, False]  # Valider, Annuler

        form = ConstructeurFormulaire("test", title="Mon Titre")
        form.fields = []

        form.render()

        mock_md.assert_called_with("### Mon Titre")

    @patch("streamlit.text_input", return_value="Test")
    @patch("streamlit.markdown")
    @patch("streamlit.form")
    @patch("streamlit.columns")
    @patch("streamlit.form_submit_button")
    def test_render_submit_valid(self, mock_submit, mock_cols, mock_form, mock_md, mock_input):
        """Test render submit avec données valides."""
        from src.ui.core.base_form import ConstructeurFormulaire

        mock_form.return_value.__enter__ = MagicMock()
        mock_form.return_value.__exit__ = MagicMock()

        mock_cols.return_value = [MagicMock(), MagicMock()]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        mock_submit.side_effect = [True, False]  # Valider cliqué

        form = ConstructeurFormulaire("test")
        form.add_text("nom", "Nom", required=True)

        callback = MagicMock()
        result = form.render(on_submit=callback)

        assert result is True
        callback.assert_called_once()

    @patch("streamlit.text_input", return_value="")
    @patch("streamlit.markdown")
    @patch("streamlit.form")
    @patch("streamlit.columns")
    @patch("streamlit.form_submit_button")
    @patch("streamlit.error")
    def test_render_submit_invalid(
        self, mock_error, mock_submit, mock_cols, mock_form, mock_md, mock_input
    ):
        """Test render submit avec données invalides."""
        from src.ui.core.base_form import ConstructeurFormulaire

        mock_form.return_value.__enter__ = MagicMock()
        mock_form.return_value.__exit__ = MagicMock()

        mock_cols.return_value = [MagicMock(), MagicMock()]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        mock_submit.side_effect = [True, False]  # Valider cliqué

        form = ConstructeurFormulaire("test")
        form.add_text("nom", "Nom", required=True)

        result = form.render()

        assert result is False
        mock_error.assert_called()

    @patch("streamlit.form")
    @patch("streamlit.columns")
    @patch("streamlit.form_submit_button")
    def test_render_cancel(self, mock_submit, mock_cols, mock_form):
        """Test render annuler."""
        from src.ui.core.base_form import ConstructeurFormulaire

        mock_form.return_value.__enter__ = MagicMock()
        mock_form.return_value.__exit__ = MagicMock()

        mock_cols.return_value = [MagicMock(), MagicMock()]
        for col in mock_cols.return_value:
            col.__enter__ = MagicMock(return_value=col)
            col.__exit__ = MagicMock()

        mock_submit.side_effect = [False, True]  # Annuler cliqué

        form = ConstructeurFormulaire("test")
        form.fields = []

        callback = MagicMock()
        result = form.render(on_cancel=callback)

        assert result is False
        callback.assert_called_once()


# ═══════════════════════════════════════════════════════════
# INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestIntegration:
    """Tests d'intégration."""

    def test_exports_from_core(self):
        """Test exports depuis core."""
        from src.ui.core import ConstructeurFormulaire, FormBuilder

        assert ConstructeurFormulaire is not None
        assert FormBuilder is ConstructeurFormulaire

    def test_exports_from_ui(self):
        """Test exports depuis ui."""
        from src.ui import ConstructeurFormulaire, FormBuilder

        assert ConstructeurFormulaire is not None
        assert FormBuilder is ConstructeurFormulaire
