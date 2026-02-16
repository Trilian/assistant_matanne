"""
Footer de l'application.
"""

import streamlit as st

from src.core.config import obtenir_parametres


def afficher_footer():
    """Affiche le footer simplifié."""
    parametres = obtenir_parametres()

    st.markdown("---")

    st.caption(
        f"💚 {parametres.APP_NAME} v{parametres.APP_VERSION} | "
        f"Streamlit + Supabase + Mistral AI | ⚡ Lazy Loading"
    )
