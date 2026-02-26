"""
Module Diagnostics - Carnet de santé maison + estimation immobilière.

Fonctionnalités:
- Diagnostics immobiliers (DPE, amiante, plomb, etc.) avec alertes validité
- Estimation valeur immobilière (DVF)
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.state import rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .constants import TYPES_DIAGNOSTIC_LABELS
from .crud import (
    create_diagnostic,
    create_estimation,
    delete_diagnostic,
    get_alertes_diagnostics,
    get_all_diagnostics,
    get_all_estimations,
    get_diagnostic_by_id,
    update_diagnostic,
)
from .ui import (
    afficher_formulaire_diagnostic,
    afficher_formulaire_estimation,
    afficher_onglet_alertes,
    afficher_onglet_dashboard,
    afficher_onglet_diagnostics,
    afficher_onglet_estimation,
)

__all__ = ["app"]

_keys = KeyNamespace("diagnostics")


@profiler_rerun("diagnostics")
def app():
    """Point d'entrée du module Diagnostics."""
    with error_boundary(titre="Erreur module Diagnostics"):
        st.title("🏥 Carnet de Santé Maison")
        st.caption("Diagnostics immobiliers, DPE et estimation de valeur.")

        edit_id = st.session_state.get(_keys("edit_id"))
        if edit_id:
            diag = get_diagnostic_by_id(edit_id)
            if diag:
                label = TYPES_DIAGNOSTIC_LABELS.get(diag.type_diagnostic, diag.type_diagnostic)
                st.subheader(f"✏️ Modifier : {label}")
                afficher_formulaire_diagnostic(diag)
                if st.button("← Annuler"):
                    del st.session_state[_keys("edit_id")]
                    rerun()
                return
            else:
                del st.session_state[_keys("edit_id")]

        TAB_LABELS = [
            "📊 Vue d'ensemble",
            "📋 Diagnostics",
            "💰 Estimation",
            "⚠️ Alertes",
            "➕ Ajouter",
        ]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")
        tab1, tab2, tab3, tab4, tab5 = st.tabs(TAB_LABELS)

        with tab1:
            afficher_onglet_dashboard()
        with tab2:
            afficher_onglet_diagnostics()
        with tab3:
            afficher_onglet_estimation()
        with tab4:
            afficher_onglet_alertes()
        with tab5:
            afficher_formulaire_diagnostic()
