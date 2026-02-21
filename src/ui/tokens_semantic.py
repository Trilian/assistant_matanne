"""
Tokens sémantiques — Couche d'abstraction au-dessus des tokens bruts.

Les tokens sémantiques décrivent l'INTENTION (surface, interactive, danger…)
plutôt que la valeur brute (#ffffff). Cela permet au dark mode de cascader
automatiquement à TOUS les composants custom sans modification individuelle.

Chaque valeur est une CSS custom property (``var(--sem-*)``). Les valeurs
réelles sont injectées via ``injecter_tokens_semantiques()`` qui adapte
les mappings selon le thème clair/sombre.

Usage:
    from src.ui.tokens_semantic import Sem, injecter_tokens_semantiques

    # Dans styles.py / initialisation.py :
    injecter_tokens_semantiques()

    # Dans les composants :
    html = f'<div style="background: {Sem.SURFACE}; color: {Sem.ON_SURFACE};">...'
"""

from __future__ import annotations

from enum import StrEnum


class Sem(StrEnum):
    """Tokens sémantiques — référencent des CSS custom properties.

    Chaque valeur est un ``var(--sem-*)`` qui sera résolu côté navigateur
    selon le thème actif (clair ou sombre).
    """

    # ── Surfaces ──────────────────────────────────────────
    SURFACE = "var(--sem-surface)"
    SURFACE_ALT = "var(--sem-surface-alt)"
    SURFACE_ELEVATED = "var(--sem-surface-elevated)"
    SURFACE_OVERLAY = "var(--sem-surface-overlay)"

    # ── Texte ─────────────────────────────────────────────
    ON_SURFACE = "var(--sem-on-surface)"
    ON_SURFACE_SECONDARY = "var(--sem-on-surface-secondary)"
    ON_SURFACE_MUTED = "var(--sem-on-surface-muted)"

    # ── Interactif ────────────────────────────────────────
    INTERACTIVE = "var(--sem-interactive)"
    INTERACTIVE_HOVER = "var(--sem-interactive-hover)"
    ON_INTERACTIVE = "var(--sem-on-interactive)"

    # ── Feedback sémantique ───────────────────────────────
    SUCCESS = "var(--sem-success)"
    SUCCESS_SUBTLE = "var(--sem-success-subtle)"
    ON_SUCCESS = "var(--sem-on-success)"

    WARNING = "var(--sem-warning)"
    WARNING_SUBTLE = "var(--sem-warning-subtle)"
    ON_WARNING = "var(--sem-on-warning)"

    DANGER = "var(--sem-danger)"
    DANGER_SUBTLE = "var(--sem-danger-subtle)"
    ON_DANGER = "var(--sem-on-danger)"

    INFO = "var(--sem-info)"
    INFO_SUBTLE = "var(--sem-info-subtle)"
    ON_INFO = "var(--sem-on-info)"

    # ── Bordures ──────────────────────────────────────────
    BORDER = "var(--sem-border)"
    BORDER_SUBTLE = "var(--sem-border-subtle)"

    # ── Ombres ────────────────────────────────────────────
    SHADOW_SM = "var(--sem-shadow-sm)"
    SHADOW_MD = "var(--sem-shadow-md)"
    SHADOW_LG = "var(--sem-shadow-lg)"

    # ── Espacement composant ──────────────────────────────
    CARD_PADDING = "var(--sem-card-padding)"
    SECTION_GAP = "var(--sem-section-gap)"
    INLINE_GAP = "var(--sem-inline-gap)"


# ═══════════════════════════════════════════════════════════
# MAPPINGS LIGHT / DARK
# ═══════════════════════════════════════════════════════════

_LIGHT_MAPPING: dict[str, str] = {
    # Surfaces
    "--sem-surface": "#ffffff",
    "--sem-surface-alt": "#f8f9fa",
    "--sem-surface-elevated": "#ffffff",
    "--sem-surface-overlay": "rgba(0, 0, 0, 0.5)",
    # Texte
    "--sem-on-surface": "#212529",
    "--sem-on-surface-secondary": "#6c757d",
    "--sem-on-surface-muted": "#9e9e9e",
    # Interactif
    "--sem-interactive": "#4CAF50",
    "--sem-interactive-hover": "#388E3C",
    "--sem-on-interactive": "#ffffff",
    # Success
    "--sem-success": "#4CAF50",
    "--sem-success-subtle": "#d4edda",
    "--sem-on-success": "#155724",
    # Warning
    "--sem-warning": "#FFC107",
    "--sem-warning-subtle": "#fff3cd",
    "--sem-on-warning": "#856404",
    # Danger
    "--sem-danger": "#FF5722",
    "--sem-danger-subtle": "#f8d7da",
    "--sem-on-danger": "#721c24",
    # Info
    "--sem-info": "#2196F3",
    "--sem-info-subtle": "#e7f3ff",
    "--sem-on-info": "#0c5460",
    # Bordures
    "--sem-border": "#e2e8e5",
    "--sem-border-subtle": "#e0e0e0",
    # Ombres
    "--sem-shadow-sm": "0 2px 4px rgba(0,0,0,0.04)",
    "--sem-shadow-md": "0 4px 12px rgba(0,0,0,0.08)",
    "--sem-shadow-lg": "0 8px 25px rgba(0,0,0,0.15)",
    # Espacement
    "--sem-card-padding": "1.5rem",
    "--sem-section-gap": "2rem",
    "--sem-inline-gap": "0.5rem",
}

_DARK_MAPPING: dict[str, str] = {
    # Surfaces
    "--sem-surface": "#1a1a2e",
    "--sem-surface-alt": "#16213e",
    "--sem-surface-elevated": "#1e2a3a",
    "--sem-surface-overlay": "rgba(0, 0, 0, 0.7)",
    # Texte
    "--sem-on-surface": "#e0e0e0",
    "--sem-on-surface-secondary": "#a0a0b0",
    "--sem-on-surface-muted": "#707080",
    # Interactif
    "--sem-interactive": "#66BB6A",
    "--sem-interactive-hover": "#81C784",
    "--sem-on-interactive": "#1a1a2e",
    # Success
    "--sem-success": "#66BB6A",
    "--sem-success-subtle": "#1b3a1b",
    "--sem-on-success": "#a5d6a7",
    # Warning
    "--sem-warning": "#FFD54F",
    "--sem-warning-subtle": "#3a3520",
    "--sem-on-warning": "#ffe082",
    # Danger
    "--sem-danger": "#FF7043",
    "--sem-danger-subtle": "#3a1b1b",
    "--sem-on-danger": "#ffab91",
    # Info
    "--sem-info": "#42A5F5",
    "--sem-info-subtle": "#1b2a3a",
    "--sem-on-info": "#90caf9",
    # Bordures
    "--sem-border": "#2a3a4a",
    "--sem-border-subtle": "#1e2e3e",
    # Ombres
    "--sem-shadow-sm": "0 2px 4px rgba(0,0,0,0.2)",
    "--sem-shadow-md": "0 4px 12px rgba(0,0,0,0.3)",
    "--sem-shadow-lg": "0 8px 25px rgba(0,0,0,0.4)",
    # Espacement (identique)
    "--sem-card-padding": "1.5rem",
    "--sem-section-gap": "2rem",
    "--sem-inline-gap": "0.5rem",
}


def _generer_css_tokens(mapping: dict[str, str]) -> str:
    """Génère le bloc CSS :root avec les tokens."""
    props = "\n    ".join(f"{k}: {v};" for k, v in mapping.items())
    return f":root {{\n    {props}\n}}"


def injecter_tokens_semantiques() -> None:
    """Injecte les tokens sémantiques CSS selon le thème actif.

    Détecte automatiquement le mode (clair/sombre) depuis la session
    et injecte les variables CSS correspondantes. Appelé une fois
    dans ``initialiser_app()``.
    """
    from src.ui.theme import ModeTheme, obtenir_theme

    theme = obtenir_theme()

    if theme.mode == ModeTheme.SOMBRE:
        css = _generer_css_tokens(_DARK_MAPPING)
    elif theme.mode == ModeTheme.AUTO:
        # Utilise prefers-color-scheme pour auto-détection
        css_light = _generer_css_tokens(_LIGHT_MAPPING)
        css_dark = _generer_css_tokens(_DARK_MAPPING)
        css = f"""
{css_light}
@media (prefers-color-scheme: dark) {{
    {_generer_css_tokens(_DARK_MAPPING)}
}}
"""
    else:
        css = _generer_css_tokens(_LIGHT_MAPPING)

    from src.ui.engine import CSSManager

    CSSManager.register("tokens-semantic", css)


__all__ = [
    "Sem",
    "injecter_tokens_semantiques",
]
