"""
Module Recettes - Gestion complète des recettes
"""

import streamlit as st
from src.services.recettes import get_recette_service


def app():
    """Point d'entrée module recettes"""
    st.title("🍽️ Mes Recettes")
    st.caption("Gestion complète de votre base de recettes")

    # Sous-tabs
    tab_liste, tab_ajout, tab_ia = st.tabs(["📋 Liste", "➕ Ajouter", "✨ Générer IA"])

    with tab_liste:
        render_liste()

    with tab_ajout:
        st.info("➕ Ajouter une recette - À implémenter")

    with tab_ia:
        st.info("✨ Générer avec IA - À implémenter")


def render_liste():
    """Affiche la liste des recettes"""
    service = get_recette_service()
    
    if service is None:
        st.error("❌ Service recettes indisponible")
        return
    
    # Chercher les recettes
    recettes = service.search_advanced(limit=12)
    
    if not recettes:
        st.info("Aucune recette trouvée. Créez-en une!")
        return
    
    # Afficher en grid
    cols = st.columns(3)
    for idx, recette in enumerate(recettes):
        with cols[idx % 3]:
            st.info(
                f"**{recette.nom}**\n\n"
                f"⏱️ {recette.temps_preparation}min | "
                f"👥 {recette.portions} portions"
            )
