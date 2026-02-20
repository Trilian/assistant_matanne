"""
Thème dynamique avec persistance session_state.

Fournit un système de thème clair/sombre/auto avec:
- Persistance en session Streamlit
- Génération CSS automatique
- Compatibilité avec les Design Tokens

Usage:
    from src.ui.theme import obtenir_theme, ModeTheme, appliquer_theme

    theme = obtenir_theme()
    appliquer_theme()  # Injecte le CSS du thème actuel
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import streamlit as st

from src.ui.tokens import Couleur, Espacement, Rayon


class ModeTheme(StrEnum):
    """Modes de thème disponibles."""

    CLAIR = "clair"
    SOMBRE = "sombre"
    AUTO = "auto"


class DensiteAffichage(StrEnum):
    """Densité de l'interface."""

    COMPACT = "compact"
    NORMAL = "normal"
    CONFORTABLE = "confortable"


@dataclass
class Theme:
    """Configuration du thème graphique.

    Attributes:
        mode: Mode clair, sombre ou auto.
        accent: Couleur d'accent principale.
        rayon_bordure: Rayon des bordures par défaut.
        densite: Densité de l'affichage.
        police_personnalisee: Police personnalisée (optionnel).
    """

    mode: ModeTheme = ModeTheme.CLAIR
    accent: str = Couleur.ACCENT
    rayon_bordure: str = Rayon.LG
    densite: DensiteAffichage = DensiteAffichage.NORMAL
    police_personnalisee: str | None = None

    # ── Propriétés dérivées ────────────────────────────────

    @property
    def bg_primary(self) -> str:
        """Couleur de fond principale."""
        return Couleur.BG_SURFACE if self.mode == ModeTheme.CLAIR else "#1a1a2e"

    @property
    def bg_secondary(self) -> str:
        """Couleur de fond secondaire."""
        return Couleur.BG_SUBTLE if self.mode == ModeTheme.CLAIR else "#16213e"

    @property
    def bg_card(self) -> str:
        """Couleur de fond des cartes."""
        return Couleur.BG_SURFACE if self.mode == ModeTheme.CLAIR else "#1e2a3a"

    @property
    def text_primary(self) -> str:
        """Couleur de texte principal."""
        return Couleur.TEXT_PRIMARY if self.mode == ModeTheme.CLAIR else "#e0e0e0"

    @property
    def text_secondary(self) -> str:
        """Couleur de texte secondaire."""
        return Couleur.TEXT_SECONDARY if self.mode == ModeTheme.CLAIR else "#a0a0b0"

    @property
    def border_color(self) -> str:
        """Couleur des bordures."""
        return Couleur.BORDER if self.mode == ModeTheme.CLAIR else "#2a3a4a"

    @property
    def shadow(self) -> str:
        """Ombre par défaut."""
        if self.mode == ModeTheme.CLAIR:
            return "0 2px 4px rgba(0,0,0,0.04)"
        return "0 2px 8px rgba(0,0,0,0.3)"

    @property
    def espacement_base(self) -> str:
        """Espacement de base selon la densité."""
        mapping = {
            DensiteAffichage.COMPACT: Espacement.SM,
            DensiteAffichage.NORMAL: Espacement.MD,
            DensiteAffichage.CONFORTABLE: Espacement.LG,
        }
        return mapping[self.densite]

    # ── Génération CSS ─────────────────────────────────────

    def generer_css_variables(self) -> str:
        """Génère les variables CSS du thème."""
        font_family = self.police_personnalisee or "inherit"

        return f"""
:root {{
    --theme-bg-primary: {self.bg_primary};
    --theme-bg-secondary: {self.bg_secondary};
    --theme-bg-card: {self.bg_card};
    --theme-text-primary: {self.text_primary};
    --theme-text-secondary: {self.text_secondary};
    --theme-accent: {self.accent};
    --theme-border: {self.border_color};
    --theme-shadow: {self.shadow};
    --theme-radius: {self.rayon_bordure};
    --theme-spacing: {self.espacement_base};
    --theme-font-family: {font_family};
}}
"""

    def generer_css_complet(self) -> str:
        """Génère le CSS complet incluant variables et overrides."""
        css = self.generer_css_variables()

        if self.mode == ModeTheme.SOMBRE:
            css += """
/* Mode sombre — overrides */
.stApp {
    background-color: var(--theme-bg-primary) !important;
    color: var(--theme-text-primary) !important;
}

.stMarkdown, .stMarkdown p, .stMarkdown span {
    color: var(--theme-text-primary) !important;
}

[data-testid="stSidebar"] {
    background-color: var(--theme-bg-secondary) !important;
}

.stSelectbox label, .stTextInput label, .stNumberInput label {
    color: var(--theme-text-secondary) !important;
}

[data-testid="stExpander"] {
    background-color: var(--theme-bg-card) !important;
    border-color: var(--theme-border) !important;
}
"""

        if self.densite == DensiteAffichage.COMPACT:
            css += """
/* Densité compacte */
.stVerticalBlock > div {
    margin-bottom: 0.3rem !important;
}
.stButton > button {
    padding: 4px 12px !important;
    font-size: 0.85rem !important;
}
"""
        elif self.densite == DensiteAffichage.CONFORTABLE:
            css += """
/* Densité confortable */
.stVerticalBlock > div {
    margin-bottom: 1.2rem !important;
}
.stButton > button {
    padding: 12px 24px !important;
    font-size: 1.05rem !important;
}
"""
        return css


# ═══════════════════════════════════════════════════════════
# GESTION DU THÈME EN SESSION
# ═══════════════════════════════════════════════════════════

_SESSION_KEY = "_app_theme"


def obtenir_theme() -> Theme:
    """Retourne le thème actuel depuis la session."""
    if _SESSION_KEY not in st.session_state:
        st.session_state[_SESSION_KEY] = Theme()
    return st.session_state[_SESSION_KEY]


def definir_theme(
    mode: ModeTheme | None = None,
    accent: str | None = None,
    densite: DensiteAffichage | None = None,
    rayon_bordure: str | None = None,
    police: str | None = None,
) -> Theme:
    """Modifie le thème actuel. Seuls les paramètres non-None sont modifiés."""
    theme = obtenir_theme()

    if mode is not None:
        theme.mode = mode
    if accent is not None:
        theme.accent = accent
    if densite is not None:
        theme.densite = densite
    if rayon_bordure is not None:
        theme.rayon_bordure = rayon_bordure
    if police is not None:
        theme.police_personnalisee = police

    st.session_state[_SESSION_KEY] = theme
    return theme


def appliquer_theme() -> None:
    """Injecte le CSS du thème actuel dans la page Streamlit."""
    theme = obtenir_theme()
    css = theme.generer_css_complet()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def afficher_selecteur_theme() -> None:
    """Affiche un sélecteur de thème dans l'UI."""
    theme = obtenir_theme()

    st.markdown("### 🎨 Thème")

    col1, col2, col3 = st.columns(3)

    with col1:
        mode_options = {
            ModeTheme.CLAIR: "☀️ Clair",
            ModeTheme.SOMBRE: "🌙 Sombre",
            ModeTheme.AUTO: "🔄 Auto",
        }
        nouveau_mode = st.selectbox(
            "Mode",
            options=list(mode_options.keys()),
            format_func=lambda x: mode_options[x],
            index=list(mode_options.keys()).index(theme.mode),
            key="theme_mode_select",
        )

    with col2:
        couleurs_accent = {
            Couleur.ACCENT: "🟢 Vert (défaut)",
            Couleur.INFO: "🔵 Bleu",
            Couleur.DANGER: "🔴 Rouge",
            Couleur.WARNING: "🟡 Orange",
            Couleur.PUSH_GRADIENT_START: "🟣 Violet",
        }

        accent_keys = list(couleurs_accent.keys())
        accent_index = accent_keys.index(theme.accent) if theme.accent in accent_keys else 0

        nouveau_accent = st.selectbox(
            "Accent",
            options=accent_keys,
            format_func=lambda x: couleurs_accent[x],
            index=accent_index,
            key="theme_accent_select",
        )

    with col3:
        densite_options = {
            DensiteAffichage.COMPACT: "📐 Compact",
            DensiteAffichage.NORMAL: "📏 Normal",
            DensiteAffichage.CONFORTABLE: "🛋️ Confortable",
        }
        nouvelle_densite = st.selectbox(
            "Densité",
            options=list(densite_options.keys()),
            format_func=lambda x: densite_options[x],
            index=list(densite_options.keys()).index(theme.densite),
            key="theme_densite_select",
        )

    if (
        nouveau_mode != theme.mode
        or nouveau_accent != theme.accent
        or nouvelle_densite != theme.densite
    ):
        definir_theme(
            mode=nouveau_mode,
            accent=nouveau_accent,
            densite=nouvelle_densite,
        )
        st.rerun()


__all__ = [
    "ModeTheme",
    "DensiteAffichage",
    "Theme",
    "obtenir_theme",
    "definir_theme",
    "appliquer_theme",
    "afficher_selecteur_theme",
]
