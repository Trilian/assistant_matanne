"""
Module Courses — Gestion complète de la liste de courses.

4 onglets :
  📋 Ma Liste       — Liste active + ajout rapide
  🤖 Génération     — Depuis Planning / Inventaire / Recette
  📊 Historique     — Historique d'achats + Modèles récurrents
  🔧 Outils        — Budget / Scan Ticket / Export-Import
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.session_keys import SK
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .generation import afficher_generation
from .historique import afficher_historique_et_modeles
from .liste_active import afficher_liste_active
from .outils import afficher_outils

_keys = KeyNamespace("courses")

TAB_LABELS = [
    "📋 Ma Liste",
    "🤖 Génération",
    "📊 Historique & Modèles",
    "🔧 Outils",
]


@profiler_rerun("courses")
def app():
    """Point d'entrée module courses."""
    st.title("🛒 Courses")
    st.caption("Gestion de votre liste de courses")

    if SK.COURSES_REFRESH not in st.session_state:
        st.session_state[SK.COURSES_REFRESH] = 0

    tab_index = tabs_with_url(TAB_LABELS, param="tab")
    tab_liste, tab_generation, tab_historique, tab_outils = st.tabs(TAB_LABELS)

    with tab_liste:
        with error_boundary(titre="Erreur liste active"):
            afficher_liste_active()

    with tab_generation:
        with error_boundary(titre="Erreur génération"):
            afficher_generation()

    with tab_historique:
        with error_boundary(titre="Erreur historique"):
            afficher_historique_et_modeles()

    with tab_outils:
        with error_boundary(titre="Erreur outils"):
            afficher_outils()


__all__ = ["app"]
