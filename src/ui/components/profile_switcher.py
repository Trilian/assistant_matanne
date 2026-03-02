"""
Sélecteur de profil utilisateur — affiché dans la sidebar.

Permet le switch rapide entre Anne et Mathieu.
"""

from __future__ import annotations

import logging

import streamlit as st

logger = logging.getLogger(__name__)


def afficher_selecteur_profil() -> None:
    """Affiche le sélecteur de profil dans la sidebar."""
    from src.core.state import obtenir_etat, rerun

    etat = obtenir_etat()

    # Indicateur IA Active — visible sur toutes les pages via la sidebar
    ia_css = (
        "background: #e8f5e9; color: #2E7D32; border: 1px solid #a5d6a7; "
        "border-radius: 999px; padding: 3px 10px; font-size: 0.78rem; "
        "font-weight: 600; display: inline-block; margin-bottom: 2px;"
    )
    ia_indispo_css = (
        "background: #fff8e1; color: #f57c00; border: 1px solid #ffe082; "
        "border-radius: 999px; padding: 3px 10px; font-size: 0.78rem; "
        "font-weight: 600; display: inline-block; margin-bottom: 2px;"
    )
    if etat.agent_ia:
        st.markdown(f'<span style="{ia_css}">🤖 IA Active</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span style="{ia_indispo_css}">🤖 IA Indispo</span>', unsafe_allow_html=True)

    # Charger les profils depuis la DB (cache en session)
    if "profils_disponibles" not in st.session_state:
        try:
            from src.services.profils import ProfilService

            profils = ProfilService.obtenir_profils()
            st.session_state["profils_disponibles"] = [
                {
                    "username": p.username,
                    "display_name": p.display_name,
                    "avatar": p.avatar_emoji,
                }
                for p in profils
            ]
        except Exception:
            logger.debug("Chargement profils DB échoué, fallback par défaut")
            st.session_state["profils_disponibles"] = [
                {"username": "anne", "display_name": "Anne", "avatar": "👩"},
                {"username": "mathieu", "display_name": "Mathieu", "avatar": "👨"},
            ]

    profils = st.session_state["profils_disponibles"]
    if not profils:
        return

    # Trouver l'index du profil actif
    noms_affichage = [f"{p['avatar']} {p['display_name']}" for p in profils]
    index_actuel = 0
    for i, p in enumerate(profils):
        if (
            p["display_name"] == etat.nom_utilisateur
            or p["username"] == etat.nom_utilisateur.lower()
        ):
            index_actuel = i
            break

    # Sélecteur
    st.markdown(
        """
        <style>
        [data-testid="stSidebarUserContent"] { padding-top: 0.25rem !important; }
        </style>
        <div style="margin-top: 2px;">
        """,
        unsafe_allow_html=True,
    )
    choix = st.selectbox(
        "👤 Profil actif",
        noms_affichage,
        index=index_actuel,
        key="sidebar_profil_selecteur",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Déterminer le profil sélectionné
    idx = noms_affichage.index(choix)
    profil_choisi = profils[idx]

    # Changer de profil si différent
    if profil_choisi["display_name"] != etat.nom_utilisateur:
        try:
            from src.services.profils import ProfilService

            if ProfilService.changer_profil_actif(profil_choisi["username"]):
                # Invalider le cache pour forcer un rechargement
                st.session_state.pop("profils_disponibles", None)
                rerun()
        except Exception as e:
            logger.error("Erreur changement de profil: %s", e)
            st.error(f"Erreur: {e}")
