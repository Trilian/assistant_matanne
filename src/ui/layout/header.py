"""
Header de l'application.
"""

import streamlit as st

from src.core.config import obtenir_parametres
from src.core.state import obtenir_etat
from src.ui import badge


def afficher_header():
    """Affiche le header avec badges d'état."""
    parametres = obtenir_parametres()
    etat = obtenir_etat()

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.markdown(
            f"<div class='main-header'>"
            f"<h1>ðŸ¤– {parametres.APP_NAME}</h1>"
            f"<p style='color: var(--secondary); margin: 0;'>"
            f"Assistant familial intelligent"
            f"</p></div>",
            unsafe_allow_html=True,
        )

    with col2:
        if etat.agent_ia:
            badge("ðŸ¤– IA Active", "#4CAF50")
        else:
            badge("ðŸ¤– IA Indispo", "#FFC107")

    with col3:
        if etat.notifications_non_lues > 0:
            if st.button(f"ðŸ”” {etat.notifications_non_lues}"):
                st.session_state.show_notifications = True
