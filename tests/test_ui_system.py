"""
Tests pour le système UI.

Tests des modules:
- system.css (StyleSheet)
- testing (SnapshotTester)
"""

import pytest


class TestStyleSheet:
    """Tests pour le moteur CSS."""

    def test_create_class_deterministic(self):
        """Test que les classes sont déterministes."""
        from src.ui.engine import StyleSheet

        StyleSheet.reset()

        class1 = StyleSheet.create_class({"display": "flex", "gap": "1rem"})
        class2 = StyleSheet.create_class({"display": "flex", "gap": "1rem"})

        assert class1 == class2
        assert class1.startswith("css-")

    def test_create_class_different_styles(self):
        """Test que styles différents = classes différentes."""
        from src.ui.engine import StyleSheet

        StyleSheet.reset()

        class1 = StyleSheet.create_class({"display": "flex"})
        class2 = StyleSheet.create_class({"display": "block"})

        assert class1 != class2

    def test_underscore_to_dash(self):
        """Test conversion underscore â†’ tiret."""
        from src.ui.engine import StyleSheet

        StyleSheet.reset()

        StyleSheet.create_class({"border_radius": "8px"})
        css = StyleSheet.get_all_css()

        assert "border-radius" in css
        assert "border_radius" not in css

    def test_styled_helper(self):
        """Test le helper styled()."""
        from src.ui.engine import styled

        html = styled("div", display="flex", gap="1rem")

        assert html.startswith("<div")
        assert 'class="css-' in html

    def test_styled_with_attrs(self):
        """Test styled_with_attrs() avec attributs ARIA."""
        from src.ui.engine import styled_with_attrs

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
        from src.ui.engine import css_class

        class_name = css_class(display="flex", gap="1rem")

        assert class_name.startswith("css-")


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
