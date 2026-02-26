"""Styles CSS pour le module Projets."""

import streamlit as st

from src.ui.tokens import Couleur


def injecter_css_projets():
    """Injecte le CSS spécifique au module Projets."""
    st.markdown(
        f"""
        <style>
        .projet-card {{
            border: 1px solid {Couleur.BORDER_LIGHT};
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 0.8rem;
            background: var(--background-color, white);
            transition: transform 0.2s ease;
        }}
        .projet-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        .projet-badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .badge-haute {{ background: {Couleur.BG_LIGHT_RED}; color: {Couleur.SCALE_CRITICAL}; }}
        .badge-moyenne {{ background: {Couleur.BG_LIGHT_ORANGE}; color: {Couleur.SCALE_BAD}; }}
        .badge-basse {{ background: {Couleur.BG_LIGHT_GREEN}; color: {Couleur.SCALE_GOOD}; }}
        .badge-en_cours {{ background: {Couleur.BG_JULES_START}; color: {Couleur.JULES_PRIMARY}; }}
        .badge-termine {{ background: {Couleur.BG_LIGHT_GREEN}; color: {Couleur.SCALE_GOOD}; }}
        .badge-annule {{ background: {Couleur.BG_GREY_100}; color: {Couleur.GREY_600}; }}
        .materiel-item {{
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
            border-bottom: 1px solid {Couleur.BG_HOVER};
        }}
        .roi-card {{
            text-align: center;
            padding: 1.2rem;
            border-radius: 10px;
            background: linear-gradient(135deg, {Couleur.BG_LIGHT_GREEN} 0%, {Couleur.BG_LIGHT_GREEN_ALT} 100%);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
