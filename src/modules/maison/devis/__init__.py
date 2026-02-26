"""Module Devis Comparatifs - Comparaison de devis artisans."""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.state import rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .constants import STATUTS_DEVIS_LABELS
from .crud import (
    create_devis,
    delete_devis,
    get_all_devis,
    get_devis_by_id,
    update_devis,
)
from .ui import (
    afficher_formulaire_devis,
    afficher_onglet_comparaison,
    afficher_onglet_devis,
)

__all__ = ["app"]

_keys = KeyNamespace("devis")


@profiler_rerun("devis")
def app():
    """Point d'entrée du module Devis Comparatifs."""
    with error_boundary(titre="Erreur module Devis"):
        st.title("📑 Devis Comparatifs")
        st.caption("Comparez vos devis artisans et choisissez le meilleur.")

        edit_id = st.session_state.get(_keys("edit_id"))
        if edit_id:
            devis = get_devis_by_id(edit_id)
            if devis:
                st.subheader("✏️ Modifier le devis")
                afficher_formulaire_devis(devis)
                if st.button("← Annuler"):
                    del st.session_state[_keys("edit_id")]
                    rerun()
                return
            else:
                del st.session_state[_keys("edit_id")]

        TAB_LABELS = ["📋 Mes Devis", "⚖️ Comparer", "➕ Ajouter"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")
        tab1, tab2, tab3 = st.tabs(TAB_LABELS)

        with tab1:
            afficher_onglet_devis()
        with tab2:
            afficher_onglet_comparaison()
        with tab3:
            afficher_formulaire_devis()
