"""
Module Énergie - Suivi détaillé de la consommation énergétique.

Complète le module Charges en offrant:
- Suivi mensuel des consommations (kWh, m³, L)
- Graphiques de tendances
- Comparaison année N vs N-1
- Objectifs de réduction
- Alertes sur-consommation
"""

import streamlit as st

from src.core.db import obtenir_contexte_db  # Re-export pour tests
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

# Re-exports pour compatibilité
from .constants import ENERGIES, MOIS_FR, MOIS_NOMS, TYPES_ENERGIE
from .data import charger_historique_energie, get_stats_energie
from .graphiques import (
    graphique_comparaison_annees,
    graphique_evolution,
    graphique_repartition,
)
from .ui import (
    afficher_alertes,
    afficher_dashboard_global,
    afficher_detail_energie,
    afficher_metric_energie,
    afficher_onglet_dashboard,
    afficher_onglet_objectifs,
    afficher_onglet_saisie,
    afficher_onglet_tendances,
)

__all__ = ["app"]

_keys = KeyNamespace("energie")


@profiler_rerun("energie")
def app():
    """Point d'entrée du module Énergie."""
    st.title("⚡ Suivi Énergie")
    st.caption("Suivez et optimisez votre consommation énergétique mensuelle.")

    # Init session state
    if _keys("consommations") not in st.session_state:
        st.session_state[_keys("consommations")] = []

    TAB_LABELS = [
        "📊 Dashboard",
        "⚡ Électricité",
        "🔥 Gaz",
        "💧 Eau",
        "🚨 Alertes",
    ]
    tabs_with_url(TAB_LABELS, param="tab")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(TAB_LABELS)

    with tab1:
        with error_boundary(titre="Erreur dashboard énergie"):
            afficher_dashboard_global()
            col1, col2 = st.columns(2)
            with col1:
                fig = graphique_repartition()
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        with error_boundary(titre="Erreur détail électricité"):
            afficher_detail_energie("electricite")

    with tab3:
        with error_boundary(titre="Erreur détail gaz"):
            afficher_detail_energie("gaz")

    with tab4:
        with error_boundary(titre="Erreur détail eau"):
            afficher_detail_energie("eau")

    with tab5:
        with error_boundary(titre="Erreur alertes"):
            afficher_alertes()
