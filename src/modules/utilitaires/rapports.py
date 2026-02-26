"""
Module Rapports PDF - Interface Streamlit

Hub orchestrateur. Les onglets sont dans:
- rapports_stocks.py
- rapports_budget.py
- rapports_gaspillage.py
- rapports_historique.py
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.state.url import tabs_with_url

from .rapports_budget import afficher_rapport_budget
from .rapports_gaspillage import afficher_analyse_gaspillage
from .rapports_historique import afficher_historique

# Re-export pour compatibilite arriere
from .rapports_stocks import afficher_rapport_stocks, get_rapports_service

# ═══════════════════════════════════════════════════════════
# MODULE PRINCIPAL
# ═══════════════════════════════════════════════════════════


@profiler_rerun("rapports")
def app():
    """Point d'entree module rapports PDF"""

    st.title("📊 Rapports PDF")
    st.markdown("Générez des rapports professionnels pour votre gestion")
    st.markdown("---")

    # Onglets
    TAB_LABELS = ["📦 Stocks", "💡 Budget", "🎯 Gaspillage", "🗑️ Historique"]
    tabs_with_url(TAB_LABELS, param="tab")
    tab1, tab2, tab3, tab4 = st.tabs(TAB_LABELS)

    with tab1:
        with error_boundary(titre="Erreur rapport stocks"):
            afficher_rapport_stocks()

    with tab2:
        with error_boundary(titre="Erreur rapport budget"):
            afficher_rapport_budget()

    with tab3:
        with error_boundary(titre="Erreur analyse gaspillage"):
            afficher_analyse_gaspillage()

    with tab4:
        with error_boundary(titre="Erreur historique"):
            afficher_historique()


# ═══════════════════════════════════════════════════════════
# PAGE ENTRY
# ═══════════════════════════════════════════════════════════


if __name__ == "__main__":
    app()
