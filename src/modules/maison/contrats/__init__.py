"""
Module Contrats - Suivi contrats maison.

Fonctionnalités:
- Dashboard des contrats actifs avec coût total mensuel
- Alertes de renouvellement / résiliation
- CRUD contrats avec tous types (assurance, énergie, box, etc.)
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.state import rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .constants import STATUTS_CONTRAT_LABELS, TYPES_CONTRAT_LABELS
from .crud import (
    create_contrat,
    delete_contrat,
    get_alertes_contrats,
    get_all_contrats,
    get_contrat_by_id,
    get_resume_financier,
    update_contrat,
)
from .ui import (
    afficher_formulaire_contrat,
    afficher_onglet_alertes,
    afficher_onglet_contrats,
    afficher_onglet_dashboard,
)

__all__ = ["app"]

_keys = KeyNamespace("contrats")


@profiler_rerun("contrats")
def app():
    """Point d'entrée du module Contrats."""
    with error_boundary(titre="Erreur module Contrats"):
        st.title("📋 Contrats & Abonnements")
        st.caption("Gérez vos contrats maison : assurance, énergie, box, téléphone...")

        # Mode édition
        edit_id = st.session_state.get(_keys("edit_id"))
        if edit_id:
            contrat = get_contrat_by_id(edit_id)
            if contrat:
                st.subheader(f"✏️ Modifier : {contrat.nom}")
                afficher_formulaire_contrat(contrat)
                if st.button("← Annuler"):
                    del st.session_state[_keys("edit_id")]
                    rerun()
                return
            else:
                del st.session_state[_keys("edit_id")]

        # Onglets
        TAB_LABELS = ["📊 Dashboard", "📋 Contrats", "🔔 Alertes", "➕ Ajouter"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")
        tab1, tab2, tab3, tab4 = st.tabs(TAB_LABELS)

        with tab1:
            afficher_onglet_dashboard()
        with tab2:
            afficher_onglet_contrats()
        with tab3:
            afficher_onglet_alertes()
        with tab4:
            afficher_formulaire_contrat()
