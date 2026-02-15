"""
Module Recettes - Gestion complète des recettes

Fonctionnalités:
- Liste des recettes avec filtres et pagination
- Détail recette avec badges, historique et versions
- Ajout manuel de recettes
- Génération de recettes avec l'IA
- Génération d'images pour les recettes
"""

import streamlit as st

from src.services.recettes import get_recette_service

# Import externe pour l'onglet import
from ..recettes_import import render_importer
from .ajout import render_ajouter_manuel
from .detail import render_detail_recette
from .generation_ia import render_generer_ia

# Imports des sous-modules
from .liste import render_liste
from .utils import formater_quantite


def app():
    """Point d'entrée module recettes"""
    st.title("🍽️ Mes Recettes")
    st.caption("Gestion complète de votre base de recettes")

    # Gérer l'état de la vue détails
    if "detail_recette_id" not in st.session_state:
        st.session_state.detail_recette_id = None

    # Si une recette est sélectionnée, afficher son détail
    if st.session_state.detail_recette_id is not None:
        service = get_recette_service()
        if service is not None:
            recette = service.get_by_id_full(st.session_state.detail_recette_id)
            if recette:
                # Bouton retour en haut avec icône visible
                col_retour, col_titre = st.columns([1, 10])
                with col_retour:
                    if st.button("⬅️", help="Retour à la liste", use_container_width=True):
                        st.session_state.detail_recette_id = None
                        st.rerun()
                with col_titre:
                    st.write(f"**{recette.nom}**")
                st.divider()
                render_detail_recette(recette)
                return
        st.error("❌ Recette non trouvée")
        st.session_state.detail_recette_id = None

    # Sous-tabs avec persistence d'état
    if "recettes_selected_tab" not in st.session_state:
        st.session_state.recettes_selected_tab = 0

    tab_liste, tab_ajout, tab_import, tab_ia = st.tabs(
        ["📋 Liste", "➕ Ajouter Manuel", "📥 Importer", "⏰ Générer IA"]
    )

    with tab_liste:
        st.session_state.recettes_selected_tab = 0
        render_liste()

    with tab_ajout:
        st.session_state.recettes_selected_tab = 1
        render_ajouter_manuel()

    with tab_import:
        st.session_state.recettes_selected_tab = 2
        render_importer()

    with tab_ia:
        st.session_state.recettes_selected_tab = 3
        render_generer_ia()


__all__ = [
    "app",
    "render_liste",
    "render_detail_recette",
    "render_ajouter_manuel",
    "render_generer_ia",
    "formater_quantite",
]
