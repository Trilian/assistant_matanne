"""
Styles CSS pour l'application.

Utilise les **Tokens Sémantiques** (``Sem``) pour garantir la cohérence
visuelle et le support automatique du dark mode. Les anciennes variables
CSS (``--primary``, ``--accent``…) sont conservées comme **alias** vers
``--sem-*`` pour rétrocompatibilité.

Enregistre le CSS dans le :class:`CSSManager` au lieu d'injecter
directement via ``st.markdown``.
"""

from src.ui.engine import CSSManager
from src.ui.tokens import (
    Couleur,
    Espacement,
    Ombre,
    Rayon,
    Transition,
    Typographie,
)


def injecter_css():
    """Enregistre les styles CSS globaux dans le CSSManager.

    Les variables CSS legacy (``--primary``, ``--accent``…) sont bridgées
    vers les tokens sémantiques ``--sem-*`` pour que le dark mode cascade
    automatiquement sans modifier chaque composant individuellement.
    """
    CSSManager.register(
        "global-styles",
        f"""
:root {{
    /* ── Bridge legacy vars → semantic tokens ──────────── */
    --primary: {Couleur.PRIMARY};
    --secondary: {Couleur.SECONDARY};
    --accent: var(--sem-interactive, {Couleur.ACCENT});
    --text-primary: var(--sem-on-surface, {Couleur.TEXT_PRIMARY});
    --text-secondary: var(--sem-on-surface-secondary, {Couleur.TEXT_SECONDARY});
    --bg-surface: var(--sem-surface, {Couleur.BG_SURFACE});
    --bg-subtle: var(--sem-surface-alt, {Couleur.BG_SUBTLE});
    --border: var(--sem-border, {Couleur.BORDER});
    --success: var(--sem-success, {Couleur.SUCCESS});
    --warning: var(--sem-warning, {Couleur.WARNING});
    --danger: var(--sem-danger, {Couleur.DANGER});
    --info: var(--sem-info, {Couleur.INFO});
}}

/* Focus visible — accessibilité */
*:focus-visible {{
    outline: 2px solid var(--sem-interactive, {Couleur.ACCENT});
    outline-offset: 2px;
}}

/* Reduced motion — accessibilité */
@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }}
}}

.main-header {{
    padding: {Espacement.MD} 0;
    border-bottom: 2px solid var(--sem-interactive, {Couleur.ACCENT});
    margin-bottom: {Espacement.XL};
}}

.metric-card {{
    background: var(--sem-surface, {Couleur.BG_SURFACE});
    padding: {Espacement.LG};
    border-radius: {Rayon.LG};
    box-shadow: var(--sem-shadow-sm, {Ombre.SM});
    transition: transform {Transition.NORMAL};
}}

.metric-card:hover {{
    transform: translateY(-2px);
}}

/* Cartes de navigation */
.nav-card {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    color: var(--sem-on-interactive, white);
    padding: {Espacement.LG};
    border-radius: {Rayon.LG};
    text-align: center;
    cursor: pointer;
    transition: all {Transition.SLOW};
}}

.nav-card:hover {{
    transform: translateY(-4px);
    box-shadow: var(--sem-shadow-lg, {Ombre.LG});
}}

/* Badges */
.badge {{
    display: inline-block;
    padding: {Espacement.XS} 0.75rem;
    border-radius: {Rayon.XXL};
    font-size: 0.85rem;
    font-weight: 500;
}}

.badge-success {{
    background: var(--sem-success-subtle, {Couleur.BG_SUCCESS});
    color: var(--sem-on-success, {Couleur.BADGE_SUCCESS_TEXT});
}}

.badge-warning {{
    background: var(--sem-warning-subtle, {Couleur.BG_WARNING});
    color: var(--sem-on-warning, {Couleur.BADGE_WARNING_TEXT});
}}

.badge-danger {{
    background: var(--sem-danger-subtle, {Couleur.BG_DANGER});
    color: var(--sem-on-danger, {Couleur.BADGE_DANGER_TEXT});
}}

/* Boutons — éviter que les labels se replient sur plusieurs lignes */
.stButton > button {{
    white-space: nowrap !important;
    overflow: hidden;
    text-overflow: ellipsis;
    min-height: 36px;
    padding: 8px 12px;
}}

/* Masquer éléments Streamlit par défaut */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}

/* ══════════════════════════════════════════════════════ */
/* RESPONSIVE — Mobile first breakpoints                  */
/* ══════════════════════════════════════════════════════ */

/* Smartphones (< 480px) */
@media (max-width: 480px) {{
    .main-header h1 {{
        font-size: clamp(1.2rem, 4vw, 1.5rem);
    }}

    .metric-card {{
        padding: {Espacement.SM};
    }}

    .nav-card {{
        padding: {Espacement.MD};
        font-size: {Typographie.BODY_SM};
    }}

    /* Streamlit columns → stack en mobile */
    [data-testid="column"] {{
        min-width: 100% !important;
    }}

    /* Boutons pleine largeur */
    .stButton > button {{
        font-size: {Typographie.BODY_SM} !important;
        padding: 8px 12px !important;
    }}
}}

/* Petites tablettes (480px — 768px) */
@media (min-width: 481px) and (max-width: 768px) {{
    .main-header h1 {{
        font-size: 1.5rem;
    }}

    .metric-card {{
        padding: {Espacement.MD};
    }}

    [data-testid="column"] {{
        min-width: 48% !important;
    }}
}}

/* Tablettes + desktop (> 768px) */
@media (min-width: 769px) {{
    .main-header h1 {{
        font-size: clamp(1.5rem, 3vw, 2rem);
    }}
}}

/* Typographie fluide */
html {{
    font-size: clamp(14px, 1.5vw, 16px);
}}

/* ══════════════════════════════════════════════════════ */
/* PRINT — Impression propre des recettes/plannings       */
/* ══════════════════════════════════════════════════════ */

@media print {{
    /* Masquer navigation et éléments interactifs */
    [data-testid="stSidebar"],
    [data-testid="stToolbar"],
    .stButton,
    .stDownloadButton,
    #MainMenu,
    footer,
    header {{
        display: none !important;
    }}

    /* Fond blanc, texte noir */
    .stApp {{
        background: white !important;
        color: black !important;
    }}

    /* Pas de coupure dans les cartes */
    .metric-card, .nav-card, [data-testid="stExpander"] {{
        break-inside: avoid;
        page-break-inside: avoid;
    }}

    /* Réinitialiser les ombres et bordures */
    * {{
        box-shadow: none !important;
        text-shadow: none !important;
    }}

    /* Colonnes en lignes empilées */
    [data-testid="column"] {{
        min-width: 100% !important;
    }}
}}
""",
    )
