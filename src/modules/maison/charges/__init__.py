"""
Module Charges - Suivi des charges et énergie.

Sous-module pour le suivi des dépenses énergétiques et charges fixes.
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .db_access import charger_factures
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


def _charger_donnees_charges():
    """Charge les factures depuis la DB, avec fallback session_state."""
    if _keys("factures") not in st.session_state or st.session_state.get("_charges_reload", True):
        st.session_state[_keys("factures")] = charger_factures()
        st.session_state._charges_reload = False

    return st.session_state[_keys("factures")]


@profiler_rerun("charges")
def app():
    """Point d'entrée du module Charges gamifié."""
    injecter_css_charges()

    # Charger depuis la DB (avec cache session_state)
    factures = _charger_donnees_charges()

    if _keys("badges_vus") not in st.session_state:
        st.session_state[_keys("badges_vus")] = []

    # Header
    afficher_header()

    # Onglets enrichis avec deep linking
    TAB_LABELS = [
        "\U0001f4ca Dashboard",
        "\U0001f4c4 Factures",
        "\U0001f4c8 Analyse",
        "\U0001f4b0 Simulation",
        "\U0001f4a1 Conseils",
    ]
    tabs_with_url(TAB_LABELS, param="tab")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(TAB_LABELS)

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
