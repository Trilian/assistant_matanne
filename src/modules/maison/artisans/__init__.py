"""
Module Artisans - Carnet d'adresses artisans avec historique interventions.

Fonctionnalités:
- Carnet d'adresses artisans par métier
- Historique des interventions et coûts
- Notes de satisfaction et recommandations
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.state import rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .constants import METIERS_LABELS
from .crud import (
    create_artisan,
    create_intervention,
    delete_artisan,
    get_all_artisans,
    get_artisan_by_id,
    get_stats_artisans,
    update_artisan,
)
from .ui import (
    afficher_formulaire_artisan,
    afficher_formulaire_intervention,
    afficher_onglet_artisans,
    afficher_onglet_dashboard,
    afficher_onglet_interventions,
)

__all__ = ["app"]

_keys = KeyNamespace("artisans")


@profiler_rerun("artisans")
def app():
    """Point d'entrée du module Artisans."""
    with error_boundary(titre="Erreur module Artisans"):
        st.title("👷 Carnet d'Artisans")
        st.caption("Gérez votre carnet d'adresses artisans et l'historique des interventions.")

        # Mode édition
        edit_id = st.session_state.get(_keys("edit_id"))
        if edit_id:
            artisan = get_artisan_by_id(edit_id)
            if artisan:
                st.subheader(f"✏️ Modifier : {artisan.nom}")
                afficher_formulaire_artisan(artisan)
                if st.button("← Annuler"):
                    del st.session_state[_keys("edit_id")]
                    rerun()
                return
            else:
                del st.session_state[_keys("edit_id")]

        TAB_LABELS = ["📊 Récap", "📒 Artisans", "🔧 Interventions", "➕ Ajouter"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")
        tab1, tab2, tab3, tab4 = st.tabs(TAB_LABELS)

        with tab1:
            afficher_onglet_dashboard()
        with tab2:
            afficher_onglet_artisans()
        with tab3:
            afficher_onglet_interventions()
        with tab4:
            afficher_formulaire_artisan()
