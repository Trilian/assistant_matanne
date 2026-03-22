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

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.session_keys import SK
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

# Nouveaux sous-modules
from .budget_ui import afficher_budget_courses
from .export_drive_ui import afficher_export_drive
from .historique import afficher_historique

# Imports des sous-modules
from .liste_active import (
    afficher_ajouter_article,
    afficher_liste_active,
    afficher_print_view,
    afficher_rayon_articles,
)
from .mode_rapide_ui import afficher_mode_rapide
from .modeles import afficher_modeles
from .outils import afficher_outils
from .planning import afficher_courses_depuis_planning
from .realtime import (
    _init_realtime_sync,
    afficher_realtime_status,
)
from .scan_ticket_ui import afficher_scan_ticket
from .suggestions_ia import afficher_suggestions_ia
from .utils import PRIORITY_EMOJIS, RAYONS_DEFAULT

# Session keys scopées
_keys = KeyNamespace("courses")


@profiler_rerun("courses")
def app():
    """Point d'entrée module courses"""
    st.title("🛒 Courses")
    st.caption("Gestion de votre liste de courses")

    # Initialiser session state
    if SK.COURSES_REFRESH not in st.session_state:
        st.session_state[SK.COURSES_REFRESH] = 0
    if _keys("new_article_mode") not in st.session_state:
        st.session_state[_keys("new_article_mode")] = False
    # Initialiser la synchronisation temps réel
    _init_realtime_sync()

    # Afficher le panneau collaboratif dans la sidebar
    try:
        from src.ui.views.synchronisation import afficher_panneau_collaboratif

        afficher_panneau_collaboratif()
    except Exception:
        pass  # Sync non configurée, mode solo

    # Tabs principales avec deep linking URL
    TAB_LABELS = [
        "📋 Liste Active",
        "🍽️ Depuis Planning",
        "⏰ Suggestions IA",
        "📋 Historique",
        "📄 Modèles",
        "💰 Budget",
        "⚡ Mode Rapide",
        "🧾 Scan Ticket",
        "🚗 Export Drive",
        "🔧 Outils",
    ]
    tab_index = tabs_with_url(TAB_LABELS, param="tab")
    (
        tab_liste,
        tab_planning,
        tab_suggestions,
        tab_historique,
        tab_modeles,
        tab_budget,
        tab_rapide,
        tab_ticket,
        tab_drive,
        tab_outils,
    ) = st.tabs(TAB_LABELS)

    with tab_liste:
        with error_boundary(titre="Erreur liste active"):
            afficher_liste_active()

    with tab_planning:
        with error_boundary(titre="Erreur planning courses"):
            afficher_courses_depuis_planning()

    with tab_suggestions:
        with error_boundary(titre="Erreur suggestions IA"):
            afficher_suggestions_ia()

    with tab_historique:
        with error_boundary(titre="Erreur historique"):
            afficher_historique()

    with tab_modeles:
        with error_boundary(titre="Erreur modèles"):
            afficher_modeles()

    with tab_budget:
        with error_boundary(titre="Erreur budget"):
            afficher_budget_courses()

    with tab_rapide:
        with error_boundary(titre="Erreur mode rapide"):
            afficher_mode_rapide()

    with tab_ticket:
        with error_boundary(titre="Erreur scan ticket"):
            afficher_scan_ticket()

    with tab_drive:
        with error_boundary(titre="Erreur export drive"):
            afficher_export_drive()

    with tab_outils:
        with error_boundary(titre="Erreur outils"):
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
