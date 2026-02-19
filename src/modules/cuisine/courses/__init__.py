"""
Module Courses - Gestion complète de la liste de courses

Fonctionnalités complètes:
- Gestion CRUD complète de la liste
- Intégration inventaire (stock bas → courses)
- Suggestions IA par recettes
- Historique & modèles récurrents
- Partage & synchronisation multi-appareils
- Synchronisation temps réel entre utilisateurs
"""

import streamlit as st

# Re-export constants depuis _common
from ._common import PRIORITY_EMOJIS, RAYONS_DEFAULT
from .historique import afficher_historique

# Imports des sous-modules
from .liste_active import (
    afficher_ajouter_article,
    afficher_liste_active,
    afficher_print_view,
    afficher_rayon_articles,
)
from .modeles import afficher_modeles
from .outils import afficher_outils
from .planning import afficher_courses_depuis_planning
from .realtime import (
    _init_realtime_sync,
    afficher_realtime_status,
)
from .suggestions_ia import afficher_suggestions_ia


def app():
    """Point d'entrée module courses"""
    st.title("🛒 Courses")
    st.caption("Gestion de votre liste de courses")

    # Initialiser session state
    if "courses_refresh" not in st.session_state:
        st.session_state.courses_refresh = 0
    if "new_article_mode" not in st.session_state:
        st.session_state.new_article_mode = False
    if "courses_active_tab" not in st.session_state:
        st.session_state.courses_active_tab = 0

    # Initialiser la synchronisation temps réel
    _init_realtime_sync()

    # Tabs principales
    tab_liste, tab_planning, tab_suggestions, tab_historique, tab_modeles, tab_outils = st.tabs(
        [
            "📋 Liste Active",
            "🍽️ Depuis Planning",
            "⏰ Suggestions IA",
            "📋 Historique",
            "📄 Modèles",
            "🔧 Outils",
        ]
    )

    with tab_liste:
        st.session_state.courses_active_tab = 0
        afficher_liste_active()

    with tab_planning:
        st.session_state.courses_active_tab = 1
        afficher_courses_depuis_planning()

    with tab_suggestions:
        st.session_state.courses_active_tab = 2
        afficher_suggestions_ia()

    with tab_historique:
        st.session_state.courses_active_tab = 3
        afficher_historique()

    with tab_modeles:
        st.session_state.courses_active_tab = 4
        afficher_modeles()

    with tab_outils:
        st.session_state.courses_active_tab = 5
        afficher_outils()


__all__ = [
    "app",
    "afficher_liste_active",
    "afficher_rayon_articles",
    "afficher_ajouter_article",
    "afficher_print_view",
    "afficher_courses_depuis_planning",
    "afficher_suggestions_ia",
    "afficher_historique",
    "afficher_modeles",
    "afficher_outils",
    "afficher_realtime_status",
    "PRIORITY_EMOJIS",
    "RAYONS_DEFAULT",
]
