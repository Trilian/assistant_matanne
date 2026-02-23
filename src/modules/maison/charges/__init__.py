"""
Module Charges - Suivi des charges et énergie.

Sous-module pour le suivi des dépenses énergétiques et charges fixes.
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

from .onglets import (
    onglet_analyse,
    onglet_conseils,
    onglet_dashboard,
    onglet_factures,
    onglet_simulation,
)
from .styles import injecter_css_charges
from .ui import afficher_header

__all__ = ["app"]

_keys = KeyNamespace("charges")


@profiler_rerun("charges")
def app():
    """Point d'entrée du module Charges gamifié."""
    injecter_css_charges()

    # Initialiser les données en session
    if _keys("factures") not in st.session_state:
        st.session_state[_keys("factures")] = []

    if _keys("badges_vus") not in st.session_state:
        st.session_state[_keys("badges_vus")] = []

    factures = st.session_state[_keys("factures")]

    # Header
    afficher_header()

    # Onglets enrichis
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📊 Dashboard", "📄 Factures", "📈 Analyse", "💰 Simulation", "💡 Conseils"]
    )

    with tab1:
        with error_boundary(titre="Erreur dashboard charges"):
            onglet_dashboard(factures)

    with tab2:
        with error_boundary(titre="Erreur factures"):
            onglet_factures(factures)

    with tab3:
        with error_boundary(titre="Erreur analyse charges"):
            onglet_analyse(factures)

    with tab4:
        with error_boundary(titre="Erreur simulation"):
            onglet_simulation(factures)

    with tab5:
        with error_boundary(titre="Erreur conseils"):
            onglet_conseils()
