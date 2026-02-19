"""
Module Inventaire - Gestion du stock

Fonctionnalités complètes:
- Gestion complète du stock avec alertes
- Catégorisation et filtres avancés
- Suggestions IA pour les courses
- Export/Import des données
- Prédictions ML et recommandations
- Notifications d'alertes
- Gestion des photos
"""

import streamlit as st

from .alertes import afficher_alertes
from .categories import afficher_categories
from .historique import afficher_historique
from .notifications import afficher_notifications, afficher_notifications_widget
from .photos import afficher_photos
from .predictions import afficher_predictions

# Imports des sous-modules
from .stock import afficher_add_article_form, afficher_stock
from .suggestions import afficher_suggestions_ia
from .tools import afficher_tools


def app():
    """Point d'entrée module inventaire"""
    col_title, col_help = st.columns([10, 1])
    with col_title:
        st.title("📦 Inventaire")
    with col_help:
        st.markdown(
            "<span title=\"Gérez votre stock d'ingrédients, suivez les dates de péremption, "
            "recevez des alertes et optimisez vos courses grâce à l'IA.\" "
            'style="cursor: help; font-size: 1.5rem;">❓</span>',
            unsafe_allow_html=True,
        )
    st.caption("Gestion complète de votre stock d'ingrédients")

    # Initialiser session state
    if "show_form" not in st.session_state:
        st.session_state.show_form = False
    if "refresh_counter" not in st.session_state:
        st.session_state.refresh_counter = 0

    # Tabs principales
    (
        tab_stock,
        tab_alertes,
        tab_categories,
        tab_suggestions,
        tab_historique,
        tab_photos,
        tab_notifications,
        tab_predictions,
        tab_tools,
    ) = st.tabs(
        [
            "📊 Stock",
            "⚠️ Alertes",
            "🏷️ Catégories",
            "🛒 Suggestions IA",
            "📋 Historique",
            "📷 Photos",
            "🔔 Notifications",
            "🔮 Prévisions",
            "🔧 Outils",
        ]
    )

    with tab_stock:
        afficher_stock()

    with tab_alertes:
        afficher_alertes()

    with tab_categories:
        afficher_categories()

    with tab_suggestions:
        afficher_suggestions_ia()

    with tab_historique:
        afficher_historique()

    with tab_photos:
        afficher_photos()

    with tab_notifications:
        afficher_notifications()

    with tab_predictions:
        afficher_predictions()

    with tab_tools:
        afficher_tools()

    # Afficher formulaire d'ajout si demandé
    if st.session_state.show_form:
        st.divider()
        afficher_add_article_form()


__all__ = [
    "app",
    "afficher_stock",
    "afficher_add_article_form",
    "afficher_alertes",
    "afficher_categories",
    "afficher_suggestions_ia",
    "afficher_photos",
    "afficher_notifications",
    "afficher_notifications_widget",
    "afficher_predictions",
    "afficher_tools",
    "afficher_historique",
]
