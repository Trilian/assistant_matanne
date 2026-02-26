"""
Module Presse-papiers Partagé — Post-its numériques entre membres.

Zone de notes partagées type "frigo numérique" pour laisser
des messages entre membres de la famille.
"""

import logging

import streamlit as st

from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.services.utilitaires.service import get_presse_papiers_service
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("presse_papiers")

AUTEURS = ["Matanne", "Papa", "Maman", "Jules"]

COULEURS_POSTIT = [
    ("#fff9c4", "🟡 Jaune"),
    ("#bbdefb", "🔵 Bleu"),
    ("#c8e6c9", "🟢 Vert"),
    ("#ffe0b2", "🟠 Orange"),
    ("#f8bbd0", "🌸 Rose"),
    ("#e1bee7", "🟣 Violet"),
]


@profiler_rerun("presse_papiers")
def app():
    """Point d'entrée module Presse-papiers Partagé."""
    st.title("📋 Presse-papiers Partagé")
    st.caption("Laissez des messages sur le frigo numérique 🧲")

    with error_boundary(titre="Erreur presse-papiers"):
        service = get_presse_papiers_service()

        # Formulaire rapide d'ajout
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                contenu = st.text_input(
                    "✍️ Nouveau message",
                    placeholder="N'oublie pas de sortir les poubelles...",
                    key=_keys("new_contenu"),
                    label_visibility="collapsed",
                )
            with col2:
                auteur = st.selectbox(
                    "De",
                    options=AUTEURS,
                    key=_keys("new_auteur"),
                    label_visibility="collapsed",
                )
            with col3:
                if st.button("📌 Épingler", key=_keys("post"), use_container_width=True):
                    if contenu:
                        service.ajouter(contenu=contenu, auteur=auteur)
                        st.rerun()

        st.divider()

        # Liste des messages
        messages = service.lister()

        if not messages:
            st.info("🧲 Le frigo est vide ! Laissez un premier message ci-dessus.")
            return

        st.caption(f"📋 {len(messages)} message(s) épinglé(s)")

        # Affichage en grille post-it style
        cols = st.columns(3)
        for i, msg in enumerate(messages):
            couleur_bg = COULEURS_POSTIT[i % len(COULEURS_POSTIT)][0]
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(
                        f"<div style='background-color:{couleur_bg};padding:8px;border-radius:6px;'>"
                        f"<p style='margin:0;font-size:1.1em;'>{msg.contenu}</p>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        date_str = msg.cree_le.strftime("%d/%m %H:%M") if msg.cree_le else ""
                        st.caption(f"— {msg.auteur or 'Anonyme'} • {date_str}")
                    with col_b:
                        if st.button("❌", key=_keys("del", str(msg.id)), help="Retirer"):
                            service.supprimer(msg.id)
                            st.rerun()
