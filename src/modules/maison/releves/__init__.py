"""Module Relevés Compteurs - Suivi eau, électricité, gaz."""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.state import rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .constants import TYPES_COMPTEUR_LABELS, UNITES_COMPTEUR
from .crud import create_releve, get_all_releves, get_stats_releves
from .ui import (
    afficher_formulaire_releve,
    afficher_onglet_dashboard,
    afficher_onglet_historique,
)

__all__ = ["app"]

_keys = KeyNamespace("releves")


@profiler_rerun("releves")
def app():
    """Point d'entrée du module Relevés Compteurs."""
    with error_boundary(titre="Erreur module Relevés Compteurs"):
        st.title("📊 Relevés Compteurs")
        st.caption("Suivez vos consommations eau, électricité, gaz et détectez les anomalies.")

        TAB_LABELS = ["📈 Dashboard", "📋 Historique", "➕ Nouveau relevé"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")
        tab1, tab2, tab3 = st.tabs(TAB_LABELS)

        with tab1:
            afficher_onglet_dashboard()
        with tab2:
            afficher_onglet_historique()
        with tab3:
            afficher_formulaire_releve()
