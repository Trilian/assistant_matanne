"""
Header de l'application.
"""

import streamlit as st

from src.core.config import obtenir_parametres
from src.core.state import obtenir_etat
from src.ui.components.atoms import badge
from src.ui.tokens import Couleur, Variante
from src.ui.utils import echapper_html


def afficher_header():
    """Affiche le header avec badges d'état et skip-link d'accessibilité."""
    parametres = obtenir_parametres()
    etat = obtenir_etat()

    # Skip-link d'accessibilité (visible uniquement au focus clavier)
    st.markdown(
        '<a class="skip-link" href="#main-content">Aller au contenu principal</a>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.markdown(
            f"<div class='main-header' role='banner' aria-label='En-tête application'>"
            f"<h1>🤖 {echapper_html(parametres.APP_NAME)}</h1>"
            f"<p style='color: var(--sem-on-surface-muted, {Couleur.SECONDARY}); margin: 0;'>"
            f"Assistant familial intelligent"
            f"</p></div>",
            unsafe_allow_html=True,
        )

    # Point d'ancrage pour le skip-link
    st.markdown('<div id="main-content"></div>', unsafe_allow_html=True)

    with col2:
        if etat.agent_ia:
            badge("🤖 IA Active", variante=Variante.SUCCESS)
        else:
            badge("🤖 IA Indispo", variante=Variante.WARNING)

    with col3:
        if etat.notifications_non_lues > 0:
            if st.button(f"🔔 {etat.notifications_non_lues}"):
                st.session_state.show_notifications = True
