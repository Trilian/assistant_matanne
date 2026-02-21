"""
Tests pour les nouveaux modules UI v2.

Couvre:
- dialogs.py (DialogBuilder)
- fragments.py (ui_fragment, auto_refresh, FragmentGroup)
- layouts/ (Row, Grid, Stack)
- state/url.py (URLState)
- forms/builder.py (FormBuilder)
- engine/css.py (CSSEngine unifié)
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════
# Tests DialogBuilder
# ═══════════════════════════════════════════════════════════


class TestDialogBuilder:
    """Tests pour le builder de dialogues."""

    def test_builder_basic(self):
        """Test création basique."""
        from src.ui.dialogs import DialogBuilder

        builder = DialogBuilder("test")

        assert builder._config.key == "test"

    def test_builder_fluent_api(self):
        """Test API fluide (chaînage)."""
        from src.ui.dialogs import DialogBuilder

        builder = (
            DialogBuilder("fluent", width="large")
            .titre("Fluent Dialog")
            .message("Contenu test")
            .action("OK", primary=True)
            .action("Annuler")
        )

        assert builder._config.titre == "Fluent Dialog"
        assert builder._config.width == "large"
        assert len(builder._config.actions) == 2

    def test_confirm_dialog_helper(self):
        """Test helper confirm_dialog."""
        from src.ui.dialogs import confirm_dialog

        # Ne peut pas tester le résultat sans Streamlit runtime
        # mais vérifie que la fonction est importable
        assert callable(confirm_dialog)

    def test_alert_dialog_helper(self):
        """Test helper alert_dialog."""
        from src.ui.dialogs import alert_dialog

        assert callable(alert_dialog)

    def test_form_dialog_helper(self):
        """Test helper form_dialog."""
        from src.ui.dialogs import form_dialog

        assert callable(form_dialog)

    def test_legacy_modale_import(self):
        """Test import legacy Modale (backward compat)."""
        from src.ui import Modale

        # Modale devrait être importable
        assert Modale is not None


# ═══════════════════════════════════════════════════════════
# Tests Fragments
# ═══════════════════════════════════════════════════════════


class TestFragments:
    """Tests pour les décorateurs de fragments."""

    def test_ui_fragment_decorator(self):
        """Test décorateur @ui_fragment."""
        from src.ui.fragments import ui_fragment

        @ui_fragment
        def my_fragment():
            return "result"

        # Vérifie que c'est un callable
        assert callable(my_fragment)

    def test_auto_refresh_decorator(self):
        """Test décorateur @auto_refresh."""
        from src.ui.fragments import auto_refresh

        @auto_refresh(seconds=30)
        def live_data():
            return {"value": 42}

        assert callable(live_data)

    def test_isolated_decorator(self):
        """Test décorateur @isolated."""
        from src.ui.fragments import isolated

        @isolated
        def isolated_section():
            pass

        assert callable(isolated_section)

    def test_lazy_decorator(self):
        """Test décorateur @lazy."""
        from src.ui.fragments import lazy

        @lazy(condition=lambda: True)
        def lazy_section():
            pass

        assert callable(lazy_section)

    def test_cached_fragment_decorator(self):
        """Test décorateur @cached_fragment."""
        from src.ui.fragments import cached_fragment

        @cached_fragment(ttl=300)
        def cached_data():
            return [1, 2, 3]

        assert callable(cached_data)

    def test_fragment_group_creation(self):
        """Test création FragmentGroup."""
        from src.ui.fragments import FragmentGroup

        group = FragmentGroup("test_group")

        assert group.name == "test_group"
        assert len(group._fragments) == 0

    def test_fragment_group_register(self):
        """Test enregistrement dans FragmentGroup."""
        from src.ui.fragments import FragmentGroup

        group = FragmentGroup("dashboard")

        @group.register("metrics")
        def metrics():
            return {}

        @group.register("chart")
        def chart():
            return {}

        assert "metrics" in group._fragments
        assert "chart" in group._fragments


# ═══════════════════════════════════════════════════════════
# Tests Layouts
# ═══════════════════════════════════════════════════════════


class TestLayouts:
    """Tests pour les layouts composables."""

    def test_row_creation(self):
        """Test création Row."""
        from src.ui.layouts import Row

        row = Row(3, gap="medium")
        assert row._gap == "medium"
        assert len(row._weights) == 3

    def test_row_with_weights(self):
        """Test Row avec poids personnalisés."""
        from src.ui.layouts import Row

        row = Row([2, 1, 1])
        assert row._weights == [2, 1, 1]

    def test_grid_creation(self):
        """Test création Grid."""
        from src.ui.layouts import Grid

        grid = Grid(cols=3, gap="large")
        assert grid._cols == 3
        assert grid._gap == "large"

    def test_stack_creation(self):
        """Test création Stack."""
        from src.ui.layouts import Stack

        stack = Stack(gap="small", dividers=True)
        assert stack._gap == "small"
        assert stack._dividers is True

    def test_gap_enum(self):
        """Test énumération Gap."""
        from src.ui.layouts import Gap

        # Gap utilise les valeurs Streamlit natives
        assert Gap.XS.value == "small"
        assert Gap.SM.value == "small"
        assert Gap.MD.value == "medium"
        assert Gap.LG.value == "large"
        assert Gap.XL.value == "large"

    def test_two_columns_helper(self):
        """Test helper two_columns."""
        from src.ui.layouts import two_columns

        assert callable(two_columns)

    def test_three_columns_helper(self):
        """Test helper three_columns."""
        from src.ui.layouts import three_columns

        assert callable(three_columns)

    def test_metrics_row_helper(self):
        """Test helper metrics_row."""
        from src.ui.layouts import metrics_row

        assert callable(metrics_row)


# ═══════════════════════════════════════════════════════════
# Tests URL State
# ═══════════════════════════════════════════════════════════


class TestURLState:
    """Tests pour la synchronisation URL."""

    def test_url_state_creation(self):
        """Test création URLState."""
        from src.ui.state import URLState

        state = URLState(namespace="test")
        assert state.namespace == "test"

    def test_url_state_decorator(self):
        """Test décorateur @url_state."""
        from src.ui.state import url_state

        @url_state("tab", default="home")
        def my_page(tab):
            return tab

        assert callable(my_page)

    def test_sync_to_url_function(self):
        """Test fonction sync_to_url."""
        from src.ui.state import sync_to_url

        assert callable(sync_to_url)

    def test_get_url_param(self):
        """Test fonction get_url_param."""
        from src.ui.state import get_url_param

        assert callable(get_url_param)

    def test_set_url_param(self):
        """Test fonction set_url_param."""
        from src.ui.state import set_url_param

        assert callable(set_url_param)

    def test_pagination_with_url(self):
        """Test helper pagination_with_url."""
        from src.ui.state import pagination_with_url

        assert callable(pagination_with_url)

    def test_selectbox_with_url(self):
        """Test helper selectbox_with_url."""
        from src.ui.state import selectbox_with_url

        assert callable(selectbox_with_url)


# ═══════════════════════════════════════════════════════════
# Tests Form Builder
# ═══════════════════════════════════════════════════════════


class TestFormBuilder:
    """Tests pour le builder de formulaires."""

    def test_builder_creation(self):
        """Test création FormBuilder."""
        from src.ui.forms import FormBuilder

        builder = FormBuilder("test_form")
        assert builder._key == "test_form"

    def test_builder_fluent_api(self):
        """Test API fluide."""
        from src.ui.forms import FormBuilder

        builder = (
            FormBuilder("contact")
            .text("nom", required=True)
            .text("email")
            .number("age", min_value=0)
        )

        assert len(builder._fields) == 3

    def test_builder_text_field(self):
        """Test champ texte."""
        from src.ui.forms import FormBuilder

        builder = FormBuilder("test").text(
            "username", label="Nom d'utilisateur", required=True, max_length=50
        )

        field = builder._fields[0]
        assert field.name == "username"
        assert field.label == "Nom d'utilisateur"
        assert field.required is True
        assert field.max_length == 50

    def test_builder_number_field(self):
        """Test champ numérique."""
        from src.ui.forms import FormBuilder

        builder = FormBuilder("test").number("age", label="Âge", min_value=0, max_value=120)

        field = builder._fields[0]
        assert field.name == "age"
        assert field.min_value == 0
        assert field.max_value == 120

    def test_builder_select_field(self):
        """Test champ select."""
        from src.ui.forms import FormBuilder

        builder = FormBuilder("test").select("pays", label="Pays", options=["FR", "BE", "CH"])

        field = builder._fields[0]
        assert field.name == "pays"
        assert field.options == ["FR", "BE", "CH"]

    def test_form_result_dataclass(self):
        """Test dataclass FormResult."""
        from src.ui.forms import FormResult

        result = FormResult(submitted=True, data={"name": "Test"}, errors={})

        assert result.submitted is True
        assert result.data["name"] == "Test"
        assert result.is_valid is True

    def test_form_result_with_errors(self):
        """Test FormResult avec erreurs."""
        from src.ui.forms import FormResult

        result = FormResult(submitted=True, data={"name": ""}, errors={"name": "Champ requis"})

        assert result.submitted is True
        assert result.is_valid is False
        assert "name" in result.errors

    def test_creer_formulaire_helper(self):
        """Test helper creer_formulaire."""
        from src.ui.forms import creer_formulaire

        assert callable(creer_formulaire)


# ═══════════════════════════════════════════════════════════
# Tests CSSEngine
# ═══════════════════════════════════════════════════════════


class TestCSSEngine:
    """Tests pour le moteur CSS unifié."""

    def test_create_class_deterministic(self):
        """Test création de classe déterministe."""
        from src.ui.engine.css import CSSEngine

        CSSEngine.reset()

        class1 = CSSEngine.create_class({"display": "flex", "gap": "1rem"})
        class2 = CSSEngine.create_class({"display": "flex", "gap": "1rem"})

        assert class1 == class2
        assert class1.startswith("css-")

    def test_create_class_different_styles(self):
        """Test classes différentes pour styles différents."""
        from src.ui.engine.css import CSSEngine

        CSSEngine.reset()

        class1 = CSSEngine.create_class({"display": "flex"})
        class2 = CSSEngine.create_class({"display": "block"})

        assert class1 != class2

    def test_underscore_to_dash(self):
        """Test conversion underscore → tiret."""
        from src.ui.engine.css import CSSEngine

        CSSEngine.reset()

        class_name = CSSEngine.create_class({"border_radius": "8px"})

        # Vérifier que la règle CSS contient border-radius
        css = CSSEngine.get_all_css()
        assert "border-radius" in css

    def test_register_block(self):
        """Test enregistrement de bloc CSS."""
        from src.ui.engine.css import CSSEngine

        CSSEngine.reset()
        CSSEngine.register("test-block", ".test { color: red; }")

        assert "test-block" in CSSEngine._blocks

    def test_unregister_block(self):
        """Test suppression de bloc CSS."""
        from src.ui.engine.css import CSSEngine

        CSSEngine.reset()
        CSSEngine.register("temp", ".temp { color: blue; }")
        CSSEngine.unregister("temp")

        assert "temp" not in CSSEngine._blocks

    def test_register_keyframes(self):
        """Test enregistrement keyframes."""
        from src.ui.engine.css import CSSEngine

        CSSEngine.reset()
        CSSEngine.register_keyframes(
            "bounce", "0% { transform: scale(1); } 50% { transform: scale(1.1); }"
        )

        assert "bounce" in CSSEngine._keyframes

    def test_styled_helper(self):
        """Test helper styled."""
        from src.ui.engine.css import CSSEngine, styled

        CSSEngine.reset()

        html = styled("div", display="flex", gap="1rem")

        assert html.startswith("<div")
        assert 'class="css-' in html

    def test_styled_with_attrs(self):
        """Test helper styled_with_attrs."""
        from src.ui.engine.css import CSSEngine, styled_with_attrs

        CSSEngine.reset()

        html = styled_with_attrs(
            "nav", attrs={"role": "navigation", "aria-label": "Menu"}, display="flex"
        )

        assert 'role="navigation"' in html
        assert 'aria-label="Menu"' in html

    def test_css_class_helper(self):
        """Test helper css_class."""
        from src.ui.engine.css import CSSEngine, css_class

        CSSEngine.reset()

        cls = css_class(display="flex", gap="1rem")

        assert cls.startswith("css-")

    def test_get_stats(self):
        """Test statistiques."""
        from src.ui.engine.css import CSSEngine

        CSSEngine.reset()
        CSSEngine.register("stats-test", ".test { color: red; }")
        CSSEngine.create_class({"display": "flex"})

        stats = CSSEngine.get_stats()

        assert stats["blocks"] >= 1
        assert stats["classes"] >= 1

    def test_backward_compat_cssmanager(self):
        """Test alias CSSManager pour backward compat."""
        from src.ui.engine.css import CSSEngine, CSSManager

        assert CSSManager is CSSEngine

    def test_backward_compat_stylesheet(self):
        """Test alias StyleSheet pour backward compat."""
        from src.ui.engine.css import CSSEngine, StyleSheet

        assert StyleSheet is CSSEngine


# ═══════════════════════════════════════════════════════════
# Tests Progress v2
# ═══════════════════════════════════════════════════════════


class TestProgressV2:
    """Tests pour progress_v2 (st.status)."""

    def test_etat_progression_enum(self):
        """Test enum EtatProgression."""
        from src.ui.feedback.progress_v2 import EtatProgression

        assert EtatProgression.EN_COURS.value == "running"
        assert EtatProgression.TERMINE.value == "complete"
        assert EtatProgression.ERREUR.value == "error"

    def test_etape_progression_dataclass(self):
        """Test dataclass EtapeProgression."""
        from src.ui.feedback.progress_v2 import EtapeProgression

        etape = EtapeProgression(nom="Test étape")

        assert etape.nom == "Test étape"
        assert etape.duree_secondes >= 0

    def test_suivi_operation_helper(self):
        """Test helper suivi_operation."""
        from src.ui.feedback.progress_v2 import suivi_operation

        assert callable(suivi_operation)

    def test_avec_progression_helper(self):
        """Test helper avec_progression."""
        from src.ui.feedback.progress_v2 import avec_progression

        assert callable(avec_progression)


# ═══════════════════════════════════════════════════════════
# Tests d'intégration imports
# ═══════════════════════════════════════════════════════════


class TestIntegrationImports:
    """Tests d'intégration pour les imports publics."""

    def test_import_dialogs_from_ui(self):
        """Test import dialogs depuis src.ui."""
        from src.ui import DialogBuilder, alert_dialog, confirm_dialog

        assert DialogBuilder is not None
        assert callable(confirm_dialog)
        assert callable(alert_dialog)

    def test_import_fragments_from_ui(self):
        """Test import fragments depuis src.ui."""
        from src.ui import FragmentGroup, auto_refresh, ui_fragment

        assert callable(ui_fragment)
        assert callable(auto_refresh)
        assert FragmentGroup is not None

    def test_import_layouts_from_ui(self):
        """Test import layouts depuis src.ui."""
        from src.ui import Gap, Grid, Row, Stack

        assert Row is not None
        assert Grid is not None
        assert Stack is not None
        assert Gap is not None

    def test_import_state_from_ui(self):
        """Test import state depuis src.ui."""
        from src.ui import URLState, get_url_param, url_state

        assert URLState is not None
        assert callable(url_state)
        assert callable(get_url_param)

    def test_import_forms_from_ui(self):
        """Test import forms depuis src.ui."""
        from src.ui import FormBuilder, FormResult

        assert FormBuilder is not None
        assert FormResult is not None

    def test_import_legacy_modale(self):
        """Test import legacy Modale."""
        from src.ui import Modale

        assert Modale is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
