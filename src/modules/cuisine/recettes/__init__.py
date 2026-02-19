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

from src.services.cuisine.recettes import obtenir_service_recettes

# Import externe pour l'onglet import
from ..recettes_import import afficher_importer
from .ajout import afficher_ajouter_manuel
from .detail import afficher_detail_recette
from .generation_ia import afficher_generer_ia

# Imports des sous-modules
from .liste import afficher_liste
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
        service = obtenir_service_recettes()
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
                afficher_detail_recette(recette)
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
        afficher_liste()

    with tab_ajout:
        st.session_state.recettes_selected_tab = 1
        afficher_ajouter_manuel()

    with tab_import:
        st.session_state.recettes_selected_tab = 2
        afficher_importer()

    with tab_ia:
        st.session_state.recettes_selected_tab = 3
        afficher_generer_ia()


__all__ = [
    "app",
    "afficher_liste",
    "afficher_detail_recette",
    "afficher_ajouter_manuel",
    "afficher_generer_ia",
    "formater_quantite",
]
