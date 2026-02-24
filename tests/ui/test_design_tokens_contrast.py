"""
Tests de contraste WCAG AA pour les tokens sémantiques.

Vérifie que toutes les paires foreground/background du design system
respectent le ratio de contraste minimum WCAG 2.1 AA (4.5:1 texte normal,
3.0:1 gros texte / éléments interactifs).
"""

import pytest

from src.ui.a11y import A11y
from src.ui.tokens_semantic import _DARK_MAPPING, _LIGHT_MAPPING

# ═══════════════════════════════════════════════════════════
# PAIRES SÉMANTIQUES FG/BG — texte normal (ratio ≥ 4.5:1)
# ═══════════════════════════════════════════════════════════

_PAIRES_TEXTE_NORMAL: list[tuple[str, str, str]] = [
    # (description, clé foreground, clé background)
    ("texte principal sur surface", "--sem-on-surface", "--sem-surface"),
    ("texte principal sur surface-alt", "--sem-on-surface", "--sem-surface-alt"),
    ("texte principal sur surface-elevated", "--sem-on-surface", "--sem-surface-elevated"),
    ("texte secondaire sur surface", "--sem-on-surface-secondary", "--sem-surface"),
    ("texte secondaire sur surface-alt", "--sem-on-surface-secondary", "--sem-surface-alt"),
    ("texte muted sur surface", "--sem-on-surface-muted", "--sem-surface"),
    # Feedback
    ("texte success sur fond success", "--sem-on-success", "--sem-success-subtle"),
    ("texte warning sur fond warning", "--sem-on-warning", "--sem-warning-subtle"),
    ("texte danger sur fond danger", "--sem-on-danger", "--sem-danger-subtle"),
    ("texte info sur fond info", "--sem-on-info", "--sem-info-subtle"),
]

# ═══════════════════════════════════════════════════════════
# PAIRES INTERACTIVES — gros texte / éléments (ratio ≥ 3.0:1)
# ═══════════════════════════════════════════════════════════

_PAIRES_INTERACTIF: list[tuple[str, str, str]] = [
    ("texte sur bouton interactif", "--sem-on-interactive", "--sem-interactive"),
]

# ═══════════════════════════════════════════════════════════
# PAIRES DÉCORATIVES — éléments non-texte (ratio ≥ 1.5:1)
# ═══════════════════════════════════════════════════════════

_PAIRES_DECORATIF: list[tuple[str, str, str]] = [
    ("bordure sur surface", "--sem-border", "--sem-surface"),
]


def _extraire_hex(mapping: dict[str, str], key: str) -> str | None:
    """Extrait une couleur hex depuis le mapping, ignore les rgba/var()."""
    val = mapping.get(key, "")
    if val.startswith("#"):
        return val
    if val.startswith("rgba") or val.startswith("var("):
        return None
    return None


# ── Thème CLAIR ───────────────────────────────────────────


class TestContrasteThemeClair:
    """Vérification des ratios de contraste en thème clair."""

    @pytest.mark.parametrize(
        "description, fg_key, bg_key",
        _PAIRES_TEXTE_NORMAL,
        ids=[p[0] for p in _PAIRES_TEXTE_NORMAL],
    )
    def test_ratio_aa_texte_normal(self, description: str, fg_key: str, bg_key: str):
        """Le ratio de contraste doit être ≥ 4.5:1 (WCAG AA texte normal)."""
        fg = _extraire_hex(_LIGHT_MAPPING, fg_key)
        bg = _extraire_hex(_LIGHT_MAPPING, bg_key)

        if fg is None or bg is None:
            pytest.skip(f"Couleur non-hex ignorée: fg={fg}, bg={bg}")

        ratio = A11y.ratio_contraste(fg, bg)
        assert ratio >= 4.5, f"[CLAIR] {description}: ratio {ratio:.2f} < 4.5 ({fg} sur {bg})"

    @pytest.mark.parametrize(
        "description, fg_key, bg_key",
        _PAIRES_INTERACTIF,
        ids=[p[0] for p in _PAIRES_INTERACTIF],
    )
    def test_ratio_aa_interactif(self, description: str, fg_key: str, bg_key: str):
        """Le ratio de contraste doit être ≥ 3.0:1 (WCAG AA gros texte / éléments)."""
        fg = _extraire_hex(_LIGHT_MAPPING, fg_key)
        bg = _extraire_hex(_LIGHT_MAPPING, bg_key)

        if fg is None or bg is None:
            pytest.skip(f"Couleur non-hex ignorée: fg={fg}, bg={bg}")

        ratio = A11y.ratio_contraste(fg, bg)
        assert ratio >= 3.0, f"[CLAIR] {description}: ratio {ratio:.2f} < 3.0 ({fg} sur {bg})"

    @pytest.mark.parametrize(
        "description, fg_key, bg_key",
        _PAIRES_DECORATIF,
        ids=[p[0] for p in _PAIRES_DECORATIF],
    )
    def test_ratio_decoratif(self, description: str, fg_key: str, bg_key: str):
        """Les éléments décoratifs (bordures) doivent être visibles (ratio ≥ 1.3:1)."""
        fg = _extraire_hex(_LIGHT_MAPPING, fg_key)
        bg = _extraire_hex(_LIGHT_MAPPING, bg_key)

        if fg is None or bg is None:
            pytest.skip(f"Couleur non-hex ignorée: fg={fg}, bg={bg}")

        ratio = A11y.ratio_contraste(fg, bg)
        assert ratio >= 1.3, f"[CLAIR] {description}: ratio {ratio:.2f} < 1.3 ({fg} sur {bg})"


# ── Thème SOMBRE ──────────────────────────────────────────


class TestContrasteThemeSombre:
    """Vérification des ratios de contraste en thème sombre."""

    @pytest.mark.parametrize(
        "description, fg_key, bg_key",
        _PAIRES_TEXTE_NORMAL,
        ids=[p[0] for p in _PAIRES_TEXTE_NORMAL],
    )
    def test_ratio_aa_texte_normal(self, description: str, fg_key: str, bg_key: str):
        """Le ratio de contraste doit être ≥ 4.5:1 (WCAG AA texte normal)."""
        fg = _extraire_hex(_DARK_MAPPING, fg_key)
        bg = _extraire_hex(_DARK_MAPPING, bg_key)

        if fg is None or bg is None:
            pytest.skip(f"Couleur non-hex ignorée: fg={fg}, bg={bg}")

        ratio = A11y.ratio_contraste(fg, bg)
        assert ratio >= 4.5, f"[SOMBRE] {description}: ratio {ratio:.2f} < 4.5 ({fg} sur {bg})"

    @pytest.mark.parametrize(
        "description, fg_key, bg_key",
        _PAIRES_INTERACTIF,
        ids=[p[0] for p in _PAIRES_INTERACTIF],
    )
    def test_ratio_aa_interactif(self, description: str, fg_key: str, bg_key: str):
        """Le ratio de contraste doit être ≥ 3.0:1 (WCAG AA gros texte / éléments)."""
        fg = _extraire_hex(_DARK_MAPPING, fg_key)
        bg = _extraire_hex(_DARK_MAPPING, bg_key)

        if fg is None or bg is None:
            pytest.skip(f"Couleur non-hex ignorée: fg={fg}, bg={bg}")

        ratio = A11y.ratio_contraste(fg, bg)
        assert ratio >= 3.0, f"[SOMBRE] {description}: ratio {ratio:.2f} < 3.0 ({fg} sur {bg})"

    @pytest.mark.parametrize(
        "description, fg_key, bg_key",
        _PAIRES_DECORATIF,
        ids=[p[0] for p in _PAIRES_DECORATIF],
    )
    def test_ratio_decoratif(self, description: str, fg_key: str, bg_key: str):
        """Les éléments décoratifs (bordures) doivent être visibles (ratio ≥ 1.3:1)."""
        fg = _extraire_hex(_DARK_MAPPING, fg_key)
        bg = _extraire_hex(_DARK_MAPPING, bg_key)

        if fg is None or bg is None:
            pytest.skip(f"Couleur non-hex ignorée: fg={fg}, bg={bg}")

        ratio = A11y.ratio_contraste(fg, bg)
        assert ratio >= 1.3, f"[SOMBRE] {description}: ratio {ratio:.2f} < 1.3 ({fg} sur {bg})"


# ── Tests utilitaires A11y ────────────────────────────────


class TestA11yUtilitaires:
    """Tests des fonctions utilitaires de contraste."""

    def test_ratio_noir_blanc(self):
        """Noir sur blanc doit avoir un ratio maximal (~21:1)."""
        ratio = A11y.ratio_contraste("#000000", "#ffffff")
        assert ratio >= 21.0

    def test_ratio_identique(self):
        """Couleurs identiques doivent avoir un ratio de 1:1."""
        ratio = A11y.ratio_contraste("#4CAF50", "#4CAF50")
        assert ratio == pytest.approx(1.0)

    def test_est_conforme_aa_texte_normal(self):
        """Noir sur blanc doit être conforme AA."""
        assert A11y.est_conforme_aa("#000000", "#ffffff") is True

    def test_non_conforme_aa(self):
        """Gris clair sur blanc ne doit PAS être conforme AA."""
        assert A11y.est_conforme_aa("#cccccc", "#ffffff") is False

    def test_conforme_aa_gros_texte(self):
        """Seuil réduit pour le gros texte (3:1 au lieu de 4.5:1)."""
        # Trouver une couleur avec ratio entre 3 et 4.5
        ratio = A11y.ratio_contraste("#767676", "#ffffff")
        assert ratio >= 3.0
        assert A11y.est_conforme_aa("#767676", "#ffffff", gros_texte=True) is True

    def test_shorthand_hex(self):
        """Support des couleurs hex abrégées (#RGB)."""
        ratio_short = A11y.ratio_contraste("#000", "#fff")
        ratio_long = A11y.ratio_contraste("#000000", "#ffffff")
        assert ratio_short == pytest.approx(ratio_long)
