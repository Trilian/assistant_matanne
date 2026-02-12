"""
Module Inventaire - Gestion du stock

FonctionnalitÃes complètes:
- Gestion complète du stock avec alertes
- CatÃegorisation et filtres avancÃes
- Suggestions IA pour les courses
- Export/Import des donnÃees
- PrÃedictions ML et recommandations
- Notifications d'alertes
- Gestion des photos
"""

import streamlit as st

# Imports des sous-modules
from .stock import render_stock, render_add_article_form
from .alertes import render_alertes
from .categories import render_categories
from .suggestions import render_suggestions_ia
from .photos import render_photos
from .notifications import render_notifications, render_notifications_widget
from .predictions import render_predictions
from .tools import render_tools
from .historique import render_historique


def app():
    """Point d'entrÃee module inventaire"""
    st.title("ðŸ“¦ Inventaire")
    st.caption("Gestion complète de votre stock d'ingrÃedients")

    # Initialiser session state
    if "show_form" not in st.session_state:
        st.session_state.show_form = False
    if "refresh_counter" not in st.session_state:
        st.session_state.refresh_counter = 0

    # Tabs principales
    tab_stock, tab_alertes, tab_categories, tab_suggestions, tab_historique, tab_photos, tab_notifications, tab_predictions, tab_tools = st.tabs([
        "ðŸ“Š Stock", 
        "âš ï¸ Alertes", 
        "ðŸ·ï¸ CatÃegories", 
        "ðŸ›’ Suggestions IA",
        "ðŸ“‹ Historique",
        "ðŸ“· Photos",
        "ðŸ”” Notifications",
        "ðŸ”® PrÃevisions",
        "ðŸ”§ Outils"
    ])

    with tab_stock:
        render_stock()

    with tab_alertes:
        render_alertes()

    with tab_categories:
        render_categories()

    with tab_suggestions:
        render_suggestions_ia()

    with tab_historique:
        render_historique()

    with tab_photos:
        render_photos()

    with tab_notifications:
        render_notifications()

    with tab_predictions:
        render_predictions()

    with tab_tools:
        render_tools()

    # Afficher formulaire d'ajout si demandÃe
    if st.session_state.show_form:
        st.divider()
        render_add_article_form()


__all__ = [
    "app",
    "render_stock",
    "render_add_article_form",
    "render_alertes",
    "render_categories",
    "render_suggestions_ia",
    "render_photos",
    "render_notifications",
    "render_notifications_widget",
    "render_predictions",
    "render_tools",
    "render_historique",
]
