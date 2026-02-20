"""
Tests pour les nouveaux modules du Design System UI.

Couvre: tokens, html_builder, registry, timer, toasts refactorisé.
"""

from __future__ import annotations

import pytest

# ═══════════════════════════════════════════════════════════
# TOKENS
# ═══════════════════════════════════════════════════════════


class TestTokens:
    """Tests pour src/ui/tokens.py."""

    def test_couleur_values_are_hex(self):
        from src.ui.tokens import Couleur

        for c in Couleur:
            assert c.value.startswith("#"), f"{c.name} = {c.value} n'est pas hex"

    def test_couleur_primary_exists(self):
        from src.ui.tokens import Couleur

        assert Couleur.PRIMARY == "#2d4d36"
        assert Couleur.SUCCESS == "#4CAF50"

    def test_espacement_values_rem(self):
        from src.ui.tokens import Espacement

        for e in Espacement:
            assert e.value.endswith("rem"), f"{e.name} = {e.value}"

    def test_rayon_values(self):
        from src.ui.tokens import Rayon

        assert Rayon.SM == "4px"
        assert Rayon.PILL == "50px"
        assert Rayon.CIRCLE == "50%"

    def test_gradient(self):
        from src.ui.tokens import gradient

        result = gradient("#000", "#fff", 90)
        assert "linear-gradient(90deg" in result
        assert "#000" in result
        assert "#fff" in result

    def test_gradient_subtil(self):
        from src.ui.tokens import gradient_subtil

        result = gradient_subtil("#4CAF50")
        assert "linear-gradient" in result
        assert "#4CAF50" in result


# ═══════════════════════════════════════════════════════════
# HTML BUILDER
# ═══════════════════════════════════════════════════════════


class TestHtmlBuilder:
    """Tests pour src/ui/html_builder.py."""

    def test_basic_div(self):
        from src.ui.html_builder import HtmlBuilder

        html = HtmlBuilder("div").text("Bonjour").build()
        assert "<div>" in html
        assert "Bonjour" in html
        assert "</div>" in html

    def test_style(self):
        from src.ui.html_builder import HtmlBuilder

        html = HtmlBuilder("span").style(color="red", padding="1rem").text("ok").build()
        assert 'style="' in html
        assert "color: red" in html
        assert "padding: 1rem" in html

    def test_child_builder(self):
        from src.ui.html_builder import HtmlBuilder

        inner = HtmlBuilder("span").text("inner")
        html = HtmlBuilder("div").child_builder(inner).build()
        assert "<div>" in html
        assert "<span>" in html
        assert "inner" in html

    def test_conditional_true(self):
        from src.ui.html_builder import HtmlBuilder

        html = HtmlBuilder("div").conditional(True, "span", text="visible").build()
        assert "visible" in html

    def test_conditional_false(self):
        from src.ui.html_builder import HtmlBuilder

        html = HtmlBuilder("div").conditional(False, lambda b: b.text("hidden")).build()
        assert "hidden" not in html

    def test_render_html(self):
        from unittest.mock import patch

        from src.ui.html_builder import render_html

        with patch("streamlit.markdown") as mock_md:
            render_html("<p>hello</p>")
            mock_md.assert_called_once_with("<p>hello</p>", unsafe_allow_html=True)

    def test_escaping(self):
        from src.ui.html_builder import HtmlBuilder

        html = HtmlBuilder("div").text("<script>alert('xss')</script>").build()
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


# ═══════════════════════════════════════════════════════════
# REGISTRY
# ═══════════════════════════════════════════════════════════


class TestRegistry:
    """Tests pour src/ui/registry.py."""

    def test_composant_ui_decorator(self):
        from src.ui.registry import composant_ui, obtenir_composant

        @composant_ui("test_cat", exemple="test_func()", tags=["test"])
        def test_func():
            """Fonction de test."""
            pass

        meta = obtenir_composant("test_func")
        assert meta is not None
        assert meta.nom == "test_func"
        assert meta.categorie == "test_cat"
        assert meta.exemple == "test_func()"
        assert "test" in meta.tags
        assert "Fonction de test." in meta.description

    def test_obtenir_catalogue(self):
        from src.ui.registry import composant_ui, obtenir_catalogue

        @composant_ui("cat_a")
        def func_a():
            pass

        catalogue = obtenir_catalogue()
        assert "cat_a" in catalogue

    def test_rechercher_composants(self):
        from src.ui.registry import composant_ui, rechercher_composants

        @composant_ui("search_test", tags=["searchable"])
        def searchable_func():
            """Recherche test."""
            pass

        results = rechercher_composants("searchable")
        assert any(m.nom == "searchable_func" for m in results)

    def test_lister_composants_par_categorie(self):
        from src.ui.registry import composant_ui, lister_composants

        @composant_ui("filter_cat")
        def filtered():
            pass

        results = lister_composants("filter_cat")
        assert any(m.nom == "filtered" for m in results)

        all_results = lister_composants()
        assert len(all_results) >= 1


# ═══════════════════════════════════════════════════════════
# FORMS - ConfigChamp
# ═══════════════════════════════════════════════════════════


class TestConfigChamp:
    """Tests pour les types de formulaires."""

    def test_type_champ_enum(self):
        from src.ui.components.forms import TypeChamp

        assert TypeChamp.TEXT == "text"
        assert TypeChamp.NUMBER == "number"
        assert TypeChamp.SELECT == "select"

    def test_config_champ_to_dict(self):
        from src.ui.components.forms import ConfigChamp, TypeChamp

        config = ConfigChamp(
            type=TypeChamp.TEXT,
            name="nom",
            label="Nom",
            required=True,
        )
        d = config.to_dict()
        assert d["type"] == "text"
        assert d["name"] == "nom"
        assert d["required"] is True

    def test_config_champ_default_label(self):
        from src.ui.components.forms import ConfigChamp

        config = ConfigChamp(name="email")
        assert config.label == "email"


# ═══════════════════════════════════════════════════════════
# TOASTS (refactorisé)
# ═══════════════════════════════════════════════════════════


class TestToasts:
    """Tests pour src/ui/feedback/toasts.py refactorisé."""

    def test_notification_internale_hash(self):
        from src.ui.feedback.toasts import _Notification

        n1 = _Notification(message="test", type_notif="success")
        n2 = _Notification(message="test", type_notif="success")
        assert n1.hash == n2.hash

        n3 = _Notification(message="other", type_notif="error")
        assert n1.hash != n3.hash

    def test_notification_frozen(self):
        from src.ui.feedback.toasts import _Notification

        n = _Notification(message="test", type_notif="info")
        with pytest.raises(AttributeError):
            n.message = "modified"
