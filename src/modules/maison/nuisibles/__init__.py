"""Module Nuisibles - Suivi traitements nuisibles."""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.state import rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .constants import TYPES_NUISIBLE_LABELS
from .crud import (
    create_traitement,
    delete_traitement,
    get_all_traitements,
    get_traitement_by_id,
    update_traitement,
)
from .ui import (
    afficher_formulaire_traitement,
    afficher_onglet_dashboard,
    afficher_onglet_historique,
)

__all__ = ["app"]

_keys = KeyNamespace("nuisibles")


@profiler_rerun("nuisibles")
def app():
    """Point d'entrée du module Nuisibles."""
    with error_boundary(titre="Erreur module Nuisibles"):
        st.title("🐜 Nuisibles & Traitements")
        st.caption("Suivez vos traitements préventifs et curatifs.")

        edit_id = st.session_state.get(_keys("edit_id"))
        if edit_id:
            t = get_traitement_by_id(edit_id)
            if t:
                st.subheader("✏️ Modifier le traitement")
                afficher_formulaire_traitement(t)
                if st.button("← Annuler"):
                    del st.session_state[_keys("edit_id")]
                    rerun()
                return
            else:
                del st.session_state[_keys("edit_id")]

        TAB_LABELS = ["📊 Récap", "📋 Historique", "➕ Ajouter"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")
        tab1, tab2, tab3 = st.tabs(TAB_LABELS)

        with tab1:
            afficher_onglet_dashboard()
        with tab2:
            afficher_onglet_historique()
        with tab3:
            afficher_formulaire_traitement()
