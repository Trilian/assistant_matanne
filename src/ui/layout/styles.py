"""
Styles CSS pour l'application.

Utilise les Design Tokens pour garantir la cohérence visuelle.
"""

import streamlit as st

from src.ui.tokens import (
    Couleur,
    Espacement,
    Ombre,
    Rayon,
    Transition,
)


def injecter_css():
    """Injecte les styles CSS modernes dans l'application en utilisant les design tokens."""
    st.markdown(
        f"""
<style>
:root {{
    --primary: {Couleur.PRIMARY};
    --secondary: {Couleur.SECONDARY};
    --accent: {Couleur.ACCENT};
    --text-primary: {Couleur.TEXT_PRIMARY};
    --text-secondary: {Couleur.TEXT_SECONDARY};
    --bg-surface: {Couleur.BG_SURFACE};
    --bg-subtle: {Couleur.BG_SUBTLE};
    --border: {Couleur.BORDER};
    --success: {Couleur.SUCCESS};
    --warning: {Couleur.WARNING};
    --danger: {Couleur.DANGER};
    --info: {Couleur.INFO};
}}

.main-header {{
    padding: {Espacement.MD} 0;
    border-bottom: 2px solid var(--accent);
    margin-bottom: {Espacement.XL};
}}

.metric-card {{
    background: var(--bg-surface);
    padding: {Espacement.LG};
    border-radius: {Rayon.LG};
    box-shadow: {Ombre.SM};
    transition: transform {Transition.NORMAL};
}}

.metric-card:hover {{
    transform: translateY(-2px);
}}

/* Cartes de navigation */
.nav-card {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    color: white;
    padding: {Espacement.LG};
    border-radius: {Rayon.LG};
    text-align: center;
    cursor: pointer;
    transition: all {Transition.SLOW};
}}

.nav-card:hover {{
    transform: translateY(-4px);
    box-shadow: {Ombre.LG};
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
    background: {Couleur.BG_SUCCESS};
    color: {Couleur.BADGE_SUCCESS_TEXT};
}}

.badge-warning {{
    background: {Couleur.BG_WARNING};
    color: {Couleur.BADGE_WARNING_TEXT};
}}

.badge-danger {{
    background: {Couleur.BG_DANGER};
    color: {Couleur.BADGE_DANGER_TEXT};
}}

/* Masquer éléments Streamlit par défaut */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}

/* Responsive */
@media (max-width: 768px) {{
    .main-header h1 {{
        font-size: 1.5rem;
    }}

    .metric-card {{
        padding: {Espacement.MD};
    }}
}}
</style>
""",
        unsafe_allow_html=True,
    )
