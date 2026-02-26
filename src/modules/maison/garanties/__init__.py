"""
Module Garanties - Suivi garanties appareils & incidents SAV.
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.state import rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .constants import STATUTS_GARANTIE_LABELS
from .crud import (
    create_garantie,
    create_incident,
    delete_garantie,
    get_alertes_garanties,
    get_all_garanties,
    get_garantie_by_id,
    get_stats_garanties,
    update_garantie,
)
from .ui import (
    afficher_formulaire_garantie,
    afficher_onglet_alertes,
    afficher_onglet_dashboard,
    afficher_onglet_garanties,
)

__all__ = ["app"]

_keys = KeyNamespace("garanties")


@profiler_rerun("garanties")
def app():
    """Point d'entrée du module Garanties & SAV."""
    with error_boundary(titre="Erreur module Garanties"):
        st.title("🛡️ Garanties & SAV")
        st.caption("Suivez vos garanties et gérez les incidents / pannes.")

        edit_id = st.session_state.get(_keys("edit_id"))
        if edit_id:
            garantie = get_garantie_by_id(edit_id)
            if garantie:
                st.subheader(f"✏️ Modifier : {garantie.nom_appareil}")
                afficher_formulaire_garantie(garantie)
                if st.button("← Annuler"):
                    del st.session_state[_keys("edit_id")]
                    rerun()
                return
            else:
                del st.session_state[_keys("edit_id")]

        TAB_LABELS = ["📊 Dashboard", "🛡️ Garanties", "⚠️ Alertes", "➕ Ajouter"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")
        tab1, tab2, tab3, tab4 = st.tabs(TAB_LABELS)

        with tab1:
            afficher_onglet_dashboard()
        with tab2:
            afficher_onglet_garanties()
        with tab3:
            afficher_onglet_alertes()
        with tab4:
            afficher_formulaire_garantie()
