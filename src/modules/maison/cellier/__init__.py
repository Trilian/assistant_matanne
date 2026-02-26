"""
Module Cellier - Inventaire cellier/garde-manger.

Fonctionnalités:
- Inventaire conserves, vins, produits secs, congelés
- Alertes DLC/DLUO
- Scan code-barres
- Seuils de réapprovisionnement
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.state import rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .constants import CATEGORIES_LABELS, UNITES
from .crud import (
    create_article,
    delete_article,
    get_alertes_peremption,
    get_alertes_stock,
    get_all_articles,
    get_article_by_id,
    get_stats_cellier,
    update_article,
)
from .ui import (
    afficher_formulaire_article,
    afficher_onglet_alertes,
    afficher_onglet_dashboard,
    afficher_onglet_inventaire,
)

__all__ = ["app"]

_keys = KeyNamespace("cellier")


@profiler_rerun("cellier")
def app():
    """Point d'entrée du module Cellier."""
    with error_boundary(titre="Erreur module Cellier"):
        st.title("🍷 Cellier & Garde-Manger")
        st.caption("Gérez votre inventaire : conserves, vins, congelés, produits secs.")

        edit_id = st.session_state.get(_keys("edit_id"))
        if edit_id:
            article = get_article_by_id(edit_id)
            if article:
                st.subheader(f"✏️ Modifier : {article.nom}")
                afficher_formulaire_article(article)
                if st.button("← Annuler"):
                    del st.session_state[_keys("edit_id")]
                    rerun()
                return
            else:
                del st.session_state[_keys("edit_id")]

        TAB_LABELS = ["📊 Dashboard", "📦 Inventaire", "⚠️ Alertes", "➕ Ajouter"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")
        tab1, tab2, tab3, tab4 = st.tabs(TAB_LABELS)

        with tab1:
            afficher_onglet_dashboard()
        with tab2:
            afficher_onglet_inventaire()
        with tab3:
            afficher_onglet_alertes()
        with tab4:
            afficher_formulaire_article()
