"""
Module Dépenses Maison - Suivi des factures (gaz, eau, électricité, etc.)

Focus sur les dépenses récurrentes de la maison avec consommation.
Fonctionnalités avancées:
- Graphiques Plotly interactifs
- Export PDF/CSV
- Prévisions IA

Utilise le service Budget unifié (src/services/budget.py).
"""

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.session_keys import SK
from src.core.state import rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .components import (
    afficher_comparaison_mois,
    afficher_depense_card,
    afficher_export_section,
    afficher_formulaire,
    afficher_graphique_evolution,
    afficher_graphique_repartition,
    afficher_onglet_ajouter,
    afficher_onglet_analyse,
    afficher_onglet_mois,
    afficher_previsions_ia,
    afficher_stats_dashboard,
)

# Import des fonctions pour exposer l'API publique
from .crud import (
    create_depense,
    delete_depense,
    get_depense_by_id,
    get_depenses_annee,
    get_depenses_mois,
    get_historique_categorie,
    get_stats_globales,
    update_depense,
)
from .utils import CATEGORY_LABELS, st

# Session keys scopées
_keys = KeyNamespace("depenses")


@profiler_rerun("depenses")
def app():
    """Point d'entrée module Dépenses"""
    st.title("💰 Dépenses Maison")
    st.caption(
        "Suivez vos dépenses: gaz, eau, électricité, loyer... avec graphiques et prévisions IA!"
    )

    # Mode édition
    if SK.EDIT_DEPENSE_ID in st.session_state:
        depense = get_depense_by_id(st.session_state[SK.EDIT_DEPENSE_ID])
        if depense:
            st.subheader(f"✏️ Modifier: {CATEGORY_LABELS.get(depense.categorie, depense.categorie)}")
            if st.button("❌ Annuler"):
                del st.session_state[SK.EDIT_DEPENSE_ID]
                rerun()
            afficher_formulaire(depense)
            del st.session_state[SK.EDIT_DEPENSE_ID]
            return

    # Dashboard
    afficher_stats_dashboard()

    st.divider()

    # Onglets enrichis avec deep linking URL
    TAB_LABELS = ["📅 Ce mois", "➕ Ajouter", "📊 Analyse"]
    tab_index = tabs_with_url(TAB_LABELS, param="tab")
    tab1, tab2, tab3 = st.tabs(TAB_LABELS)

    with tab1:
        with error_boundary(titre="Erreur ce mois"):
            afficher_onglet_mois()

    with tab2:
        with error_boundary(titre="Erreur ajout dépense"):
            afficher_onglet_ajouter()

    with tab3:
        with error_boundary(titre="Erreur analyse dépenses"):
            afficher_onglet_analyse()


__all__ = [
    # Entry point
    "app",
    # CRUD
    "get_depenses_mois",
    "get_depenses_annee",
    "get_depense_by_id",
    "create_depense",
    "update_depense",
    "delete_depense",
    "get_stats_globales",
    "get_historique_categorie",
    # UI
    "afficher_stats_dashboard",
    "afficher_depense_card",
    "afficher_formulaire",
    "afficher_graphique_evolution",
    "afficher_graphique_repartition",
    "afficher_comparaison_mois",
    "afficher_export_section",
    "afficher_previsions_ia",
    "afficher_onglet_mois",
    "afficher_onglet_ajouter",
    "afficher_onglet_analyse",
]
