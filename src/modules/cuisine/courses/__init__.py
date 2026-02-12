"""
Module Courses - Gestion complète de la liste de courses

FonctionnalitÃes complètes:
- Gestion CRUD complète de la liste
- IntÃegration inventaire (stock bas â†’ courses)
- Suggestions IA par recettes
- Historique & modèles rÃecurrents
- Partage & synchronisation multi-appareils
- Synchronisation temps rÃeel entre utilisateurs
"""

import streamlit as st

# Imports des sous-modules
from .liste_active import (
    render_liste_active,
    render_rayon_articles,
    render_ajouter_article,
    render_print_view,
)
from .planning import render_courses_depuis_planning
from .suggestions_ia import render_suggestions_ia
from .historique import render_historique
from .modeles import render_modeles
from .outils import render_outils
from .realtime import (
    _init_realtime_sync,
    render_realtime_status,
    _broadcast_article_change,
)

# Re-export constants depuis _common
from ._common import PRIORITY_EMOJIS, RAYONS_DEFAULT


def app():
    """Point d'entrÃee module courses"""
    st.title("ðŸ› Courses")
    st.caption("Gestion de votre liste de courses")

    # Initialiser session state
    if "courses_refresh" not in st.session_state:
        st.session_state.courses_refresh = 0
    if "new_article_mode" not in st.session_state:
        st.session_state.new_article_mode = False
    if "courses_active_tab" not in st.session_state:
        st.session_state.courses_active_tab = 0
    
    # Initialiser la synchronisation temps rÃeel
    _init_realtime_sync()

    # Tabs principales
    tab_liste, tab_planning, tab_suggestions, tab_historique, tab_modeles, tab_outils = st.tabs([
        "ðŸ“‹ Liste Active",
        "ðŸ½ï¸ Depuis Planning",
        "âœ¨ Suggestions IA",
        "ðŸ“š Historique",
        "ðŸ“„ Modèles",
        "ðŸ“§ Outils"
    ])

    with tab_liste:
        st.session_state.courses_active_tab = 0
        render_liste_active()

    with tab_planning:
        st.session_state.courses_active_tab = 1
        render_courses_depuis_planning()

    with tab_suggestions:
        st.session_state.courses_active_tab = 2
        render_suggestions_ia()

    with tab_historique:
        st.session_state.courses_active_tab = 3
        render_historique()

    with tab_modeles:
        st.session_state.courses_active_tab = 4
        render_modeles()

    with tab_outils:
        st.session_state.courses_active_tab = 5
        render_outils()


__all__ = [
    "app",
    "render_liste_active",
    "render_rayon_articles",
    "render_ajouter_article",
    "render_print_view",
    "render_courses_depuis_planning",
    "render_suggestions_ia",
    "render_historique",
    "render_modeles",
    "render_outils",
    "render_realtime_status",
    "PRIORITY_EMOJIS",
    "RAYONS_DEFAULT",
]
