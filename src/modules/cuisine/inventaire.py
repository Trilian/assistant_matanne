"""
Module Inventaire - Gestion du stock
"""

import streamlit as st
from src.services.inventaire import get_inventaire_service


def app():
    """Point d'entrée module inventaire"""
    st.title("📦 Inventaire")
    st.caption("Gestion de votre stock d'ingrédients")

    tab_stock, tab_categories, tab_alertes = st.tabs(["📊 Stock", "🏷️ Catégories", "⚠️ Alertes"])

    with tab_stock:
        render_stock()

    with tab_categories:
        st.info("🏷️ Gestion des catégories - À implémenter")

    with tab_alertes:
        render_alertes()


def render_stock():
    """Affiche le stock actuel"""
    service = get_inventaire_service()
    
    if service is None:
        st.error("❌ Service inventaire indisponible")
        return
    
    inventaire = service.get_inventaire_complet()
    
    if not inventaire:
        st.info("Inventaire vide. Ajoutez des articles!")
        return
    
    # Afficher les stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📦 Articles", len(inventaire))
    with col2:
        # À calculer selon les alertes
        st.metric("⚠️ Faibles", "0")
    with col3:
        # À calculer selon les périmés
        st.metric("🚨 Périmés", "0")


def render_alertes():
    """Affiche les articles en alerte"""
    st.info("⚠️ Affichage des articles alertes - À implémenter")
