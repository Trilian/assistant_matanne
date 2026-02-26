"""
Module Checklists - Checklists vacances et weekends.
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.state import rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .constants import CATEGORIES_ITEMS_LABELS, TYPES_VOYAGE_LABELS
from .crud import (
    create_checklist,
    create_from_template,
    delete_checklist,
    get_all_checklists,
    get_checklist_by_id,
    toggle_item,
)
from .ui import (
    afficher_checklist_detail,
    afficher_formulaire_checklist,
    afficher_onglet_checklists,
    afficher_onglet_templates,
)

__all__ = ["app"]

_keys = KeyNamespace("checklists")


@profiler_rerun("checklists")
def app():
    """Point d'entrée du module Checklists."""
    with error_boundary(titre="Erreur module Checklists"):
        st.title("✅ Checklists Vacances")
        st.caption("Préparez vos vacances et weekends sans rien oublier.")

        # Mode détail
        detail_id = st.session_state.get(_keys("detail_id"))
        if detail_id:
            checklist = get_checklist_by_id(detail_id)
            if checklist:
                afficher_checklist_detail(checklist)
                if st.button("← Retour"):
                    del st.session_state[_keys("detail_id")]
                    rerun()
                return
            else:
                del st.session_state[_keys("detail_id")]

        TAB_LABELS = ["📋 Mes Checklists", "📝 Depuis template", "➕ Nouvelle"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")
        tab1, tab2, tab3 = st.tabs(TAB_LABELS)

        with tab1:
            afficher_onglet_checklists()
        with tab2:
            afficher_onglet_templates()
        with tab3:
            afficher_formulaire_checklist()
