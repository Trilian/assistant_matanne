"""Module Entretien Saisonnier - Calendrier d'entretien maison."""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .constants import SAISONS_LABELS
from .crud import get_alertes_saisonnieres, get_all_entretiens, marquer_fait
from .ui import afficher_onglet_alertes, afficher_onglet_calendrier

__all__ = ["app"]

_keys = KeyNamespace("entretien_saisonnier")


@profiler_rerun("entretien_saisonnier")
def app():
    """Point d'entrée du module Entretien Saisonnier."""
    with error_boundary(titre="Erreur module Entretien Saisonnier"):
        st.title("🗓️ Entretien Saisonnier")
        st.caption("Ne ratez aucun entretien de votre maison grâce au calendrier saisonnier.")

        TAB_LABELS = ["🔔 À faire maintenant", "📅 Calendrier complet"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")
        tab1, tab2 = st.tabs(TAB_LABELS)

        with tab1:
            afficher_onglet_alertes()
        with tab2:
            afficher_onglet_calendrier()
