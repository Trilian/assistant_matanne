"""
Tests de régression visuelle pour composants UI (badge, boite_info, boule_loto).

Utilise SnapshotTester pour détecter les changements non-intentionnels
dans le rendu HTML des composants atoms.

Mise à jour des snapshots:
    UPDATE_SNAPSHOTS=1 pytest tests/test_ui_snapshots.py
"""

from __future__ import annotations

import pytest

from src.ui.components.atoms import badge_html, boite_info_html, boule_loto_html
from src.ui.testing.visual_regression import (
    SnapshotTester,
    assert_html_contains,
    assert_html_not_contains,
    normalize_html,
)
from src.ui.tokens import Couleur, Variante

# ═══════════════════════════════════════════════════════════
# BADGE — 6 variantes + couleur brute
# ═══════════════════════════════════════════════════════════


class TestBadgeSnapshots:
    """Snapshots pour le composant badge."""

    @pytest.fixture(autouse=True)
    def setup_tester(self, tmp_path, monkeypatch):
        monkeypatch.setattr(SnapshotTester, "SNAPSHOT_DIR", tmp_path)
        self.tester = SnapshotTester("badge")

    def test_badge_success(self):
        """Badge variante SUCCESS."""
        html = badge_html("Actif", variante=Variante.SUCCESS)
        self.tester.assert_matches(html, {"variant": "success"}, test_name="success")

        assert_html_contains(html, "Actif", 'role="status"', Couleur.BG_SUCCESS)

    def test_badge_warning(self):
        """Badge variante WARNING."""
        html = badge_html("En attente", variante=Variante.WARNING)
        self.tester.assert_matches(html, {"variant": "warning"}, test_name="warning")

        assert_html_contains(html, "En attente", Couleur.BG_WARNING)

    def test_badge_danger(self):
        """Badge variante DANGER."""
        html = badge_html("Expiré", variante=Variante.DANGER)
        self.tester.assert_matches(html, {"variant": "danger"}, test_name="danger")

        assert_html_contains(html, "Expiré", Couleur.BG_DANGER)

    def test_badge_info(self):
        """Badge variante INFO."""
        html = badge_html("Nouveau", variante=Variante.INFO)
        self.tester.assert_matches(html, {"variant": "info"}, test_name="info")

        assert_html_contains(html, "Nouveau", Couleur.BG_INFO)

    def test_badge_neutral(self):
        """Badge variante NEUTRAL."""
        html = badge_html("Brouillon", variante=Variante.NEUTRAL)
        self.tester.assert_matches(html, {"variant": "neutral"}, test_name="neutral")

        assert_html_contains(html, "Brouillon", Couleur.BG_HOVER)

    def test_badge_accent(self):
        """Badge variante ACCENT."""
        html = badge_html("Premium", variante=Variante.ACCENT)
        self.tester.assert_matches(html, {"variant": "accent"}, test_name="accent")

        assert_html_contains(html, "Premium", Couleur.ACCENT, "color: white")

    def test_badge_default_no_variant(self):
        """Badge sans variante → SUCCESS par défaut."""
        html = badge_html("Test")
        self.tester.assert_matches(html, {"variant": "default"}, test_name="default")

        assert_html_contains(html, "Test", Couleur.BG_SUCCESS)

    def test_badge_custom_color(self):
        """Badge avec couleur brute (rétrocompatibilité)."""
        html = badge_html("Custom", couleur="#ff0000")
        self.tester.assert_matches(html, {"couleur": "#ff0000"}, test_name="custom_color")

        assert_html_contains(html, "Custom", "#ff0000", "color: white")

    def test_badge_xss_escape(self):
        """Badge échappe les caractères dangereux."""
        html = badge_html("<script>alert('xss')</script>")

        assert_html_not_contains(html, "<script>")
        assert_html_contains(html, "&lt;script&gt;")

    def test_badge_aria_attributes(self):
        """Badge a les attributs d'accessibilité."""
        html = badge_html("Actif", variante=Variante.SUCCESS)

        assert_html_contains(html, 'role="status"', 'aria-label="Actif"')

    def test_badge_snapshot_stability(self):
        """Deux appels identiques produisent le même hash."""
        html1 = badge_html("Stable", variante=Variante.INFO)
        html2 = badge_html("Stable", variante=Variante.INFO)
        assert html1 == html2


# ═══════════════════════════════════════════════════════════
# BOITE_INFO — 4 variantes
# ═══════════════════════════════════════════════════════════


class TestBoiteInfoSnapshots:
    """Snapshots pour le composant boite_info."""

    @pytest.fixture(autouse=True)
    def setup_tester(self, tmp_path, monkeypatch):
        monkeypatch.setattr(SnapshotTester, "SNAPSHOT_DIR", tmp_path)
        self.tester = SnapshotTester("boite_info")

    def test_boite_info_default(self):
        """Boîte info variante INFO (défaut)."""
        html = boite_info_html("Astuce", "Utilisez Ctrl+S pour sauvegarder")
        self.tester.assert_matches(html, {"variante": "info"}, test_name="info_default")

        assert_html_contains(html, "Astuce", "Ctrl+S", 'role="note"')

    def test_boite_info_success(self):
        """Boîte info variante SUCCESS."""
        html = boite_info_html("Succès", "Opération terminée", "✅", variante=Variante.SUCCESS)
        self.tester.assert_matches(html, {"variante": "success"}, test_name="success")

        assert_html_contains(html, "Succès", "terminée", "✅")

    def test_boite_info_warning(self):
        """Boîte info variante WARNING."""
        html = boite_info_html("Attention", "Stock faible", "⚠️", variante=Variante.WARNING)
        self.tester.assert_matches(html, {"variante": "warning"}, test_name="warning")

        assert_html_contains(html, "Attention", "Stock faible")

    def test_boite_info_danger(self):
        """Boîte info variante DANGER."""
        html = boite_info_html("Erreur", "Connexion perdue", "❌", variante=Variante.DANGER)
        self.tester.assert_matches(html, {"variante": "danger"}, test_name="danger")

        assert_html_contains(html, "Erreur", "Connexion perdue")

    def test_boite_info_has_border_left(self):
        """Boîte info a une bordure gauche colorée."""
        html = boite_info_html("Test", "Contenu")
        assert_html_contains(html, "border-left: 4px solid")

    def test_boite_info_xss_escape(self):
        """Boîte info échappe le contenu."""
        html = boite_info_html("<b>Titre</b>", "<img src=x onerror=alert(1)>")

        assert_html_not_contains(html, "<b>Titre</b>")
        assert_html_not_contains(html, "<img")
        assert_html_contains(html, "&lt;b&gt;")

    def test_boite_info_custom_icon(self):
        """Boîte info avec icône personnalisée."""
        html = boite_info_html("Recette", "Nouvelle recette ajoutée", "🍳")

        assert_html_contains(html, "🍳")


# ═══════════════════════════════════════════════════════════
# BOULE_LOTO — normale + chance + tailles
# ═══════════════════════════════════════════════════════════


class TestBouleLotoSnapshots:
    """Snapshots pour le composant boule_loto."""

    @pytest.fixture(autouse=True)
    def setup_tester(self, tmp_path, monkeypatch):
        monkeypatch.setattr(SnapshotTester, "SNAPSHOT_DIR", tmp_path)
        self.tester = SnapshotTester("boule_loto")

    def test_boule_normale(self):
        """Boule loto normale (gradient bleu)."""
        html = boule_loto_html(7)
        self.tester.assert_matches(html, {"numero": 7, "is_chance": False}, test_name="normal_7")

        assert_html_contains(html, "7", Couleur.LOTO_NORMAL_START, 'role="img"')

    def test_boule_chance(self):
        """Boule numéro chance (gradient rose)."""
        html = boule_loto_html(3, is_chance=True)
        self.tester.assert_matches(html, {"numero": 3, "is_chance": True}, test_name="chance_3")

        assert_html_contains(html, "3", Couleur.LOTO_CHANCE_START)

    def test_boule_taille_personnalisee(self):
        """Boule avec taille personnalisée."""
        html = boule_loto_html(42, taille=60)
        self.tester.assert_matches(html, {"numero": 42, "taille": 60}, test_name="custom_size")

        assert_html_contains(html, "60px", "42")

    def test_boule_font_size_proportionnelle(self):
        """La taille de police est 40% de la taille."""
        html = boule_loto_html(1, taille=100)

        # 100 * 0.4 = 40px
        assert_html_contains(html, "font-size: 40px")

    def test_boule_aria_label(self):
        """Boule a un label d'accessibilité."""
        html = boule_loto_html(49)

        assert_html_contains(html, 'aria-label="Boule numéro 49"')

    def test_boule_round_shape(self):
        """Boule est ronde (border-radius: 50%)."""
        html = boule_loto_html(1)

        assert_html_contains(html, "border-radius: 50%")


# ═══════════════════════════════════════════════════════════
# UTILITAIRES — normalize_html, snapshot cross-check
# ═══════════════════════════════════════════════════════════


class TestSnapshotUtilities:
    """Tests pour les utilitaires de snapshot."""

    def test_normalize_html_whitespace(self):
        """normalize_html supprime les espaces multiples."""
        raw = "<div>  Hello   World  </div>"
        assert normalize_html(raw) == "<div> Hello World </div>"

    def test_normalize_html_newlines(self):
        """normalize_html unifie les retours à la ligne."""
        raw = "<div>\n  <span>\n    Text\n  </span>\n</div>"
        result = normalize_html(raw)
        assert "\n" not in result
        assert "Text" in result

    def test_snapshot_cross_component_isolation(self, tmp_path, monkeypatch):
        """Différents composants ont des snapshots séparés."""
        monkeypatch.setattr(SnapshotTester, "SNAPSHOT_DIR", tmp_path)

        badge_tester = SnapshotTester("badge")
        boule_tester = SnapshotTester("boule")

        badge_tester.assert_matches("<span>Badge</span>", {}, test_name="test1")
        boule_tester.assert_matches("<div>Boule</div>", {}, test_name="test1")

        # Les fichiers sont bien séparés
        assert (tmp_path / "badge_test1.json").exists()
        assert (tmp_path / "boule_test1.json").exists()
