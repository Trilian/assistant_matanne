"""
Design Tokens — Source unique de vérité pour couleurs, espacements, typographie.

Ce module centralise TOUTES les valeurs visuelles du design system Matanne.
Chaque composant UI doit utiliser ces tokens plutôt que des valeurs hardcodées.

Usage:
    from src.ui.tokens import Couleur, Espacement, Rayon, Typographie, Ombre

    badge(texte, couleur=Couleur.SUCCESS)
    style={"padding": Espacement.LG, "border-radius": Rayon.LG}
"""

from __future__ import annotations

from enum import StrEnum


class Couleur(StrEnum):
    """Palette de couleurs du design system."""

    # ── Primaires ──────────────────────────────────────────
    PRIMARY = "#2d4d36"
    SECONDARY = "#5e7a6a"
    ACCENT = "#4CAF50"

    # ── Sémantiques ───────────────────────────────────────
    SUCCESS = "#4CAF50"
    WARNING = "#FFC107"
    DANGER = "#FF5722"
    INFO = "#2196F3"

    # ── Texte ─────────────────────────────────────────────
    TEXT_PRIMARY = "#212529"
    TEXT_SECONDARY = "#6c757d"
    TEXT_MUTED = "#9e9e9e"

    # ── Arrière-plans ─────────────────────────────────────
    BG_SURFACE = "#ffffff"
    BG_SUBTLE = "#f8f9fa"
    BG_HOVER = "#f0f0f0"
    BG_INFO = "#e7f3ff"
    BG_SUCCESS = "#d4edda"
    BG_WARNING = "#fff3cd"
    BG_DANGER = "#f8d7da"
    BG_JULES_START = "#E3F2FD"
    BG_JULES_END = "#BBDEFB"
    BG_METEO_START = "#FFF8E1"
    BG_METEO_END = "#FFECB3"

    # ── Bordures ──────────────────────────────────────────
    BORDER = "#e2e8e5"
    BORDER_LIGHT = "#e0e0e0"
    BORDER_INFO = "#2196F3"

    # ── Graphiques ────────────────────────────────────────
    CHART_BREAKFAST = "#FFB74D"
    CHART_LUNCH = "#4CAF50"
    CHART_DINNER = "#2196F3"
    CHART_SNACK = "#E91E63"
    CHART_DEFAULT = "#9E9E9E"
    CHART_STOCK_OK = "#4CAF50"
    CHART_STOCK_BAS = "#FF5722"

    # ── Badges sémantiques ────────────────────────────────
    BADGE_SUCCESS_BG = "#d4edda"
    BADGE_SUCCESS_TEXT = "#155724"
    BADGE_WARNING_BG = "#fff3cd"
    BADGE_WARNING_TEXT = "#856404"
    BADGE_DANGER_BG = "#f8d7da"
    BADGE_DANGER_TEXT = "#721c24"

    # ── Spécifiques domaine ───────────────────────────────
    JULES_PRIMARY = "#1565C0"
    TIMER_BG_START = "#FF6B6B"
    TIMER_BG_END = "#ee5a5a"
    PUSH_GRADIENT_START = "#667eea"
    PUSH_GRADIENT_END = "#764ba2"
    NOTIFICATIONS_BADGE = "#FF4B4B"

    # ── Delta métriques ───────────────────────────────────
    DELTA_POSITIVE = "#4CAF50"
    DELTA_NEGATIVE = "#FF5722"

    # ── Gradients domaine-spécifiques ─────────────────────
    LOTO_CHANCE_START = "#f093fb"
    LOTO_CHANCE_END = "#f5576c"
    LOTO_NORMAL_START = "#667eea"
    LOTO_NORMAL_END = "#764ba2"


class Espacement(StrEnum):
    """Échelle d'espacement (en rem)."""

    XS = "0.25rem"
    SM = "0.5rem"
    MD = "1rem"
    LG = "1.5rem"
    XL = "2rem"
    XXL = "3rem"


class Rayon(StrEnum):
    """Rayons de bordure."""

    SM = "4px"
    MD = "8px"
    LG = "12px"
    XL = "16px"
    XXL = "20px"
    PILL = "50px"
    CIRCLE = "50%"


class Typographie(StrEnum):
    """Tailles typographiques."""

    CAPTION = "0.85rem"
    BODY_SM = "0.875rem"
    BODY = "1rem"
    BODY_LG = "1.2rem"
    H4 = "1.3rem"
    H3 = "1.5rem"
    H2 = "2rem"
    H1 = "2.5rem"
    DISPLAY = "4rem"
    ICON_SM = "1.3rem"
    ICON_MD = "2rem"
    ICON_LG = "2.5rem"
    ICON_XL = "3rem"


class Ombre(StrEnum):
    """Box shadows."""

    SM = "0 2px 4px rgba(0,0,0,0.04)"
    MD = "0 4px 12px rgba(0,0,0,0.08)"
    LG = "0 8px 25px rgba(0,0,0,0.15)"
    XL = "0 4px 20px rgba(0,0,0,0.1)"
    INNER = "inset 0 1px 2px rgba(0,0,0,0.06)"


class Transition(StrEnum):
    """Transitions CSS."""

    FAST = "0.15s ease"
    NORMAL = "0.2s ease"
    SLOW = "0.3s ease"
    SPRING = "0.3s cubic-bezier(0.34, 1.56, 0.64, 1)"


class ZIndex(StrEnum):
    """Z-index layers."""

    BASE = "1"
    DROPDOWN = "100"
    STICKY = "500"
    MODAL = "1000"
    TOAST = "1001"
    TOOLTIP = "1100"


class Variante(StrEnum):
    """Variantes sémantiques pour les composants.

    Permet de spécifier l'intention visuelle (succès, danger, info…)
    au lieu de couleurs brutes. Les composants mappent automatiquement
    vers les couleurs bg/text/border correspondantes.
    """

    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"
    NEUTRAL = "neutral"
    ACCENT = "accent"


def obtenir_couleurs_variante(variante: Variante) -> tuple[str, str, str]:
    """Retourne (background, text, border) pour une variante donnée.

    .. deprecated::
        Utiliser ``_obtenir_sem_variante()`` de ``atoms.py`` ou les tokens
        sémantiques ``Sem.*`` directement.  Cette fonction délègue désormais
        aux tokens sémantiques pour un rendu cohérent en dark mode.

    Args:
        variante: Variante sémantique.

    Returns:
        Tuple (couleur_fond, couleur_texte, couleur_bordure) — tokens sémantiques.
    """
    import warnings

    warnings.warn(
        "obtenir_couleurs_variante() utilise des tokens bruts. "
        "Préférer les tokens sémantiques (Sem.*) via _obtenir_sem_variante().",
        DeprecationWarning,
        stacklevel=2,
    )
    from src.ui.tokens_semantic import Sem

    _MAP: dict[Variante, tuple[str, str, str]] = {
        Variante.SUCCESS: (Sem.SUCCESS_SUBTLE, Sem.ON_SUCCESS, Sem.SUCCESS),
        Variante.WARNING: (Sem.WARNING_SUBTLE, Sem.ON_WARNING, Sem.WARNING),
        Variante.DANGER: (Sem.DANGER_SUBTLE, Sem.ON_DANGER, Sem.DANGER),
        Variante.INFO: (Sem.INFO_SUBTLE, Sem.ON_INFO, Sem.INFO),
        Variante.NEUTRAL: (Sem.SURFACE_ALT, Sem.ON_SURFACE_SECONDARY, Sem.BORDER),
        Variante.ACCENT: (Sem.INTERACTIVE, Sem.ON_INTERACTIVE, Sem.INTERACTIVE),
    }
    return _MAP.get(variante, _MAP[Variante.NEUTRAL])


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def gradient(debut: str, fin: str, angle: int = 135) -> str:
    """Génère un gradient CSS linéaire.

    Args:
        debut: Couleur de début (hex)
        fin: Couleur de fin (hex)
        angle: Angle du gradient en degrés

    Returns:
        Valeur CSS linear-gradient
    """
    return f"linear-gradient({angle}deg, {debut}, {fin})"


def gradient_subtil(couleur: str, opacite_debut: str = "15", opacite_fin: str = "05") -> str:
    """Génère un gradient subtil basé sur une couleur d'accent.

    Args:
        couleur: Couleur de base (hex)
        opacite_debut: Opacité hex du début (00-ff)
        opacite_fin: Opacité hex de la fin (00-ff)

    Returns:
        Valeur CSS linear-gradient
    """
    return f"linear-gradient(135deg, {couleur}{opacite_debut}, {couleur}{opacite_fin})"


__all__ = [
    "Couleur",
    "Espacement",
    "Rayon",
    "Typographie",
    "Ombre",
    "Transition",
    "ZIndex",
    "Variante",
    "obtenir_couleurs_variante",
    "gradient",
    "gradient_subtil",
]
