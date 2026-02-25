"""
Module Éco-Tips - Conseils écologiques pour la maison.

Conseils éco-gestes, astuces économies d'énergie et alternatives durables
avec suggestions IA personnalisées selon le profil du foyer.
Gestion CRUD des actions écologiques avec suivi des économies.
"""

import streamlit as st

from src.core.db import obtenir_contexte_db  # Re-export pour tests
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

# Re-exports pour compatibilité
from .constants import ECO_TIPS_DATA, IDEES_ACTIONS, IMPACT_COLORS, TYPE_LABELS
from .crud import (
    create_action,
    delete_action,
    get_action_by_id,
    get_all_actions,
    update_action,
)
from .stats import calculate_stats
from .ui import (
    afficher_action_card,
    afficher_formulaire,
    afficher_idees,
    afficher_onglet_ajouter,
    afficher_onglet_conseils_ia,
    afficher_onglet_eco_score,
    afficher_onglet_mes_actions,
    afficher_onglet_tips,
    afficher_stats_dashboard,
)

__all__ = ["app"]

_keys = KeyNamespace("eco_tips")


@profiler_rerun("eco_tips")
def app():
    """Point d'entrée du module Éco-Tips."""
    with error_boundary(titre="Erreur module Éco-Tips"):
        st.title("💡 Éco-Tips")
        st.caption("Adoptez des gestes simples pour réduire votre impact et vos factures.")

        # Mode édition
        edit_id = st.session_state.get(_keys("edit_id"))
        if edit_id:
            action = get_action_by_id(edit_id)
            if action:
                st.subheader(f"✏️ Modifier : {action.nom}")
                afficher_formulaire(action)
                if st.button("← Annuler"):
                    del st.session_state[_keys("edit_id")]
                    st.rerun()
                return
            else:
                # Action non trouvée — continuer normalement
                del st.session_state[_keys("edit_id")]

        # Dashboard stats
        afficher_stats_dashboard()
        st.divider()

        # Onglets
        TAB_LABELS = [
            "📋 Mes actions",
            "➕ Ajouter",
            "💡 Idées",
        ]
        tab1, tab2, tab3 = st.tabs(TAB_LABELS)

        with tab1:
            afficher_onglet_mes_actions()

        with tab2:
            afficher_onglet_ajouter()

        with tab3:
            afficher_idees()
