"""
Tests pour le système UI 3.0.

Tests des modules:
- system.variants (CVA)
- system.css (StyleSheet)
- primitives (Box, Stack, Text)
- hooks_v2 (use_state, use_query, use_form)
- testing (SnapshotTester)
"""

import pytest


class TestVariants:
    """Tests pour le système de variantes CVA."""

    def test_cva_basic(self):
        """Test création de variantes basiques."""
        from src.ui.system.variants import VariantConfig, cva

        badge = cva(
            VariantConfig(
                base="display: inline-flex; padding: 0.25rem;",
                variants={
                    "variant": {
                        "success": "background: green;",
                        "danger": "background: red;",
                    },
                },
                default_variants={"variant": "success"},
            )
        )

        # Test default
        result = badge()
        assert "display: inline-flex" in result
        assert "background: green" in result

        # Test override
        result = badge(variant="danger")
        assert "background: red" in result

    def test_cva_compound_variants(self):
        """Test des variantes composées."""
        from src.ui.system.variants import VariantConfig, cva

        button = cva(
            VariantConfig(
                base="border: none;",
                variants={
                    "intent": {
                        "primary": "background: blue;",
                        "danger": "background: red;",
                    },
                    "size": {
                        "sm": "height: 2rem;",
                        "lg": "height: 3rem;",
                    },
                },
                compound_variants=[
                    {"intent": "danger", "size": "lg", "styles": "font-weight: 700;"},
                ],
            )
        )

        # Sans compound
        result = button(intent="primary", size="lg")
        assert "font-weight: 700" not in result

        # Avec compound
        result = button(intent="danger", size="lg")
        assert "font-weight: 700" in result

    def test_tv_slots(self):
        """Test des variantes multi-slots."""
        from src.ui.system.variants import TVConfig, slot, tv

        card = tv(
            TVConfig(
                slots={
                    "root": slot("border-radius: 8px;"),
                    "header": slot("padding: 1rem;"),
                    "body": slot("padding: 1.5rem;"),
                },
                variants={
                    "variant": {
                        "elevated": {
                            "root": "box-shadow: 0 4px 8px rgba(0,0,0,0.1);",
                        },
                        "outlined": {
                            "root": "border: 1px solid gray;",
                        },
                    },
                },
                default_variants={"variant": "elevated"},
            )
        )

        styles = card()
        assert "root" in styles
        assert "header" in styles
        assert "body" in styles
        assert "box-shadow" in styles["root"]

        styles_outlined = card(variant="outlined")
        assert "border: 1px solid" in styles_outlined["root"]

    def test_badge_preset(self):
        """Test du preset badge."""
        from src.ui.system.variants import BADGE_VARIANTS, cva

        badge = cva(BADGE_VARIANTS)

        result = badge(variant="success")
        assert "#d4edda" in result or "BG_SUCCESS" in result or "background" in result

        result = badge(variant="danger")
        assert "#f8d7da" in result or "BG_DANGER" in result or "background" in result


class TestStyleSheet:
    """Tests pour le moteur CSS."""

    def test_create_class_deterministic(self):
        """Test que les classes sont déterministes."""
        from src.ui.system.css import StyleSheet

        StyleSheet.reset()

        class1 = StyleSheet.create_class({"display": "flex", "gap": "1rem"})
        class2 = StyleSheet.create_class({"display": "flex", "gap": "1rem"})

        assert class1 == class2
        assert class1.startswith("css-")

    def test_create_class_different_styles(self):
        """Test que styles différents = classes différentes."""
        from src.ui.system.css import StyleSheet

        StyleSheet.reset()

        class1 = StyleSheet.create_class({"display": "flex"})
        class2 = StyleSheet.create_class({"display": "block"})

        assert class1 != class2

    def test_underscore_to_dash(self):
        """Test conversion underscore → tiret."""
        from src.ui.system.css import StyleSheet

        StyleSheet.reset()

        StyleSheet.create_class({"border_radius": "8px"})
        css = StyleSheet.get_all_css()

        assert "border-radius" in css
        assert "border_radius" not in css

    def test_styled_helper(self):
        """Test le helper styled()."""
        from src.ui.system.css import styled

        html = styled("div", display="flex", gap="1rem")

        assert html.startswith("<div")
        assert 'class="css-' in html

    def test_styled_with_attrs(self):
        """Test styled_with_attrs() avec attributs ARIA."""
        from src.ui.system.css import styled_with_attrs

        html = styled_with_attrs(
            "nav",
            attrs={"role": "navigation", "aria-label": "Menu"},
            display="flex",
        )

        assert "<nav" in html
        assert 'role="navigation"' in html
        assert 'aria-label="Menu"' in html
        assert 'class="css-' in html

    def test_css_class_helper(self):
        """Test le helper css_class()."""
        from src.ui.system.css import css_class

        class_name = css_class(display="flex", gap="1rem")

        assert class_name.startswith("css-")


class TestPrimitives:
    """Tests pour les primitives Box, Stack, Text."""

    def test_box_basic(self):
        """Test Box basique."""
        from src.ui.primitives import Box

        box = Box(p="1rem", bg="#f8f9fa")
        box.child("<span>Hello</span>")
        html = box.html()

        assert "<div" in html
        assert "Hello" in html
        assert "</div>" in html

    def test_box_with_role(self):
        """Test Box avec attributs ARIA."""
        from src.ui.primitives import Box

        box = Box(role="navigation", aria_label="Menu principal")
        html = box.html()

        assert 'role="navigation"' in html
        assert 'aria-label="Menu principal"' in html

    def test_hstack(self):
        """Test HStack."""
        from src.ui.primitives import HStack

        stack = HStack(gap="1rem", align="center")
        stack.child("<span>A</span>")
        stack.child("<span>B</span>")
        html = stack.html()

        assert "<div" in html
        assert "A" in html
        assert "B" in html

    def test_vstack(self):
        """Test VStack."""
        from src.ui.primitives import VStack

        stack = VStack(gap="2rem")
        stack.child("<p>Premier</p>")
        stack.child("<p>Second</p>")
        html = stack.html()

        assert "Premier" in html
        assert "Second" in html

    def test_text_basic(self):
        """Test Text basique."""
        from src.ui.primitives import Text

        text = Text("Hello World", size="lg", weight="bold")
        html = text.html()

        assert "Hello World" in html
        assert "<span" in html or "class=" in html

    def test_text_escaping(self):
        """Test échappement XSS dans Text."""
        from src.ui.primitives import Text

        text = Text("<script>alert('xss')</script>")
        html = text.html()

        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_heading_helper(self):
        """Test helper heading()."""
        from src.ui.primitives.text import heading

        html = heading("Mon Titre", level=2)

        assert "<h2" in html
        assert "Mon Titre" in html

    def test_paragraph_helper(self):
        """Test helper paragraph()."""
        from src.ui.primitives.text import paragraph

        html = paragraph("Un paragraphe de texte.")

        assert "<p" in html
        assert "Un paragraphe" in html


class TestSnapshotTester:
    """Tests pour l'infrastructure de test visuel."""

    def test_snapshot_creation(self, tmp_path, monkeypatch):
        """Test création de snapshot."""
        from src.ui.testing import SnapshotTester

        # Utiliser un dossier temporaire
        monkeypatch.setattr(SnapshotTester, "SNAPSHOT_DIR", tmp_path)

        tester = SnapshotTester("test_component")

        # Premier run: crée le snapshot
        tester.assert_matches("<div>Hello</div>", {"variant": "default"})

        # Vérifier que le fichier existe
        snapshot_file = tmp_path / "test_component_default.json"
        assert snapshot_file.exists()

    def test_snapshot_match(self, tmp_path, monkeypatch):
        """Test comparaison de snapshot identique."""
        from src.ui.testing import SnapshotTester

        monkeypatch.setattr(SnapshotTester, "SNAPSHOT_DIR", tmp_path)

        tester = SnapshotTester("test_component")

        # Premier run
        tester.assert_matches("<div>Hello</div>", {"variant": "default"})

        # Second run avec même HTML: pas d'erreur
        tester.assert_matches("<div>Hello</div>", {"variant": "default"})

    def test_snapshot_mismatch(self, tmp_path, monkeypatch):
        """Test détection de changement."""
        from src.ui.testing import SnapshotTester

        monkeypatch.setattr(SnapshotTester, "SNAPSHOT_DIR", tmp_path)

        tester = SnapshotTester("test_component")

        # Premier run
        tester.assert_matches("<div>Hello</div>", {"variant": "default"})

        # Second run avec HTML différent: erreur
        with pytest.raises(AssertionError) as exc_info:
            tester.assert_matches("<div>Changed</div>", {"variant": "default"})

        assert "Snapshot mismatch" in str(exc_info.value)

    def test_assert_html_contains(self):
        """Test helper assert_html_contains."""
        from src.ui.testing.visual_regression import assert_html_contains

        html = '<div class="test"><span>Hello</span></div>'

        # Pas d'erreur
        assert_html_contains(html, "test", "Hello", "span")

        # Erreur
        with pytest.raises(AssertionError):
            assert_html_contains(html, "missing")

    def test_assert_html_not_contains(self):
        """Test helper assert_html_not_contains."""
        from src.ui.testing.visual_regression import assert_html_not_contains

        html = '<div class="safe">Content</div>'

        # Pas d'erreur
        assert_html_not_contains(html, "<script>", "onclick")

        # Erreur
        with pytest.raises(AssertionError):
            assert_html_not_contains(html, "Content")


class TestIntegration:
    """Tests d'intégration des modules UI 3.0."""

    def test_box_with_system_styles(self):
        """Test Box avec système de styles."""
        from src.ui.primitives import Box
        from src.ui.system.css import StyleSheet
        from src.ui.tokens import Couleur, Espacement

        StyleSheet.reset()

        box = Box(
            p=Espacement.LG,
            bg=Couleur.BG_SURFACE,
            radius="12px",
        )
        box.text("Contenu")
        html = box.html()

        # Vérifier que le HTML est généré
        assert "<div" in html
        assert "Contenu" in html

        # Vérifier que la classe CSS est créée
        stats = StyleSheet.get_stats()
        assert stats["total_classes"] >= 1

    def test_variant_with_box(self):
        """Test combinaison variants + Box."""
        from src.ui.primitives import Box
        from src.ui.system.css import StyleSheet
        from src.ui.system.variants import BADGE_VARIANTS, cva

        StyleSheet.reset()

        badge = cva(BADGE_VARIANTS)
        badge_styles = badge(variant="success")

        # Créer une classe à partir des styles de variante
        class_name = StyleSheet.create_from_string(badge_styles)

        assert class_name.startswith("css-")
