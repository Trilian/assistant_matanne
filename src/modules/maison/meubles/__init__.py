"""
Module Meubles - Wishlist d'achats par pièce avec budget.

Fonctionnalités:
- Wishlist de meubles/achats souhaités par pièce
- Suivi du statut (souhaité → acheté)
- Budget estimé et max par pièce
- Vue par pièce avec résumé financier
"""

import streamlit as st

from src.core.db import obtenir_contexte_db  # Re-export pour tests
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.state import rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

# Re-exports pour compatibilité
from .constants import PIECES_LABELS, PRIORITES_LABELS, STATUTS_LABELS
from .crud import (
    create_meuble,
    delete_meuble,
    get_all_meubles,
    get_budget_resume,
    get_meuble_by_id,
    update_meuble,
)
from .ui import (
    afficher_budget_summary,
    afficher_formulaire,
    afficher_meuble_card,
    afficher_onglet_ajouter,
    afficher_onglet_budget,
    afficher_onglet_wishlist,
    afficher_vue_par_piece,
)

__all__ = [
    "app",
    "PIECES_LABELS",
    "STATUTS_LABELS",
    "PRIORITES_LABELS",
    "get_all_meubles",
    "get_meuble_by_id",
    "create_meuble",
    "update_meuble",
    "delete_meuble",
    "get_budget_resume",
    "afficher_formulaire",
    "afficher_meuble_card",
    "afficher_budget_summary",
    "afficher_vue_par_piece",
    "afficher_onglet_wishlist",
    "afficher_onglet_ajouter",
    "afficher_onglet_budget",
]

_keys = KeyNamespace("meubles")


@profiler_rerun("meubles")
def app():
    """Point d'entrée du module Meubles."""
    with error_boundary(titre="Erreur module Meubles"):
        st.title("🛋️ Meubles & Achats")
        st.caption("Gérez vos achats de meubles par pièce avec suivi de budget.")

        # Mode édition
        edit_id = st.session_state.get(_keys("edit_id"))
        if edit_id:
            meuble = get_meuble_by_id(edit_id)
            if meuble:
                st.subheader(f"✏️ Modifier : {meuble.nom}")
                afficher_formulaire(meuble)
                if st.button("← Annuler"):
                    del st.session_state[_keys("edit_id")]
                    rerun()
                return
            else:
                del st.session_state[_keys("edit_id")]

        # Onglets
        TAB_LABELS = ["📋 Wishlist", "➕ Ajouter", "💰 Budget"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")
        tab1, tab2, tab3 = st.tabs(TAB_LABELS)

        with tab1:
            afficher_onglet_wishlist()

        with tab2:
            afficher_onglet_ajouter()

        with tab3:
            afficher_onglet_budget()
