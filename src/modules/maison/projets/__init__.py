"""
Module Projets Maison - Gestion des projets domestiques.

Sous-module pour planifier, estimer et suivre les projets de la maison:
- Création de projets avec estimation IA (budget, matériaux, tâches)
- Suivi de l'avancement avec timeline
- Gestion des tâches par projet
- Calcul ROI rénovations énergétiques
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .onglets import (
    onglet_creation,
    onglet_liste,
    onglet_roi,
    onglet_timeline,
)
from .styles import injecter_css_projets

__all__ = ["app"]

_keys = KeyNamespace("projets")


@profiler_rerun("projets")
def app():
    """Point d'entrée du module Projets Maison."""
    injecter_css_projets()

    st.title("🏗️ Projets Maison")
    st.caption("Planifiez, estimez et suivez vos projets domestiques avec l'aide de l'IA.")

    # Onglets avec deep linking
    TAB_LABELS = [
        "📋 Mes Projets",
        "➕ Nouveau Projet",
        "📅 Timeline",
        "💰 ROI Rénovations",
    ]
    tabs_with_url(TAB_LABELS, param="tab")
    tab1, tab2, tab3, tab4 = st.tabs(TAB_LABELS)

    with tab1:
        with error_boundary(titre="Erreur liste projets"):
            onglet_liste(_keys)

    with tab2:
        with error_boundary(titre="Erreur création projet"):
            onglet_creation(_keys)

    with tab3:
        with error_boundary(titre="Erreur timeline"):
            onglet_timeline(_keys)

    with tab4:
        with error_boundary(titre="Erreur ROI"):
            onglet_roi(_keys)
