"""
Module Dépenses Maison - Suivi des factures (gaz, eau, électricité, etc.)

Focus sur les dépenses récurrentes de la maison avec consommation.
Utilise le service Budget unifié (src/services/budget.py).
"""

from .components import (
    render_comparaison_mois,
    render_depense_card,
    render_formulaire,
    render_graphique_evolution,
    render_onglet_ajouter,
    render_onglet_analyse,
    render_onglet_mois,
    render_stats_dashboard,
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


def app():
    """Point d'entrée module Dépenses"""
    st.title("💰 Dépenses Maison")
    st.caption("Suivez vos dépenses: gaz, eau, électricité, loyer...")

    # Mode édition
    if "edit_depense_id" in st.session_state:
        depense = get_depense_by_id(st.session_state["edit_depense_id"])
        if depense:
            st.subheader(f"✏️ Modifier: {CATEGORY_LABELS.get(depense.categorie, depense.categorie)}")
            if st.button("❌ Annuler"):
                del st.session_state["edit_depense_id"]
                st.rerun()
            render_formulaire(depense)
            del st.session_state["edit_depense_id"]
            return

    # Dashboard
    render_stats_dashboard()

    st.divider()

    # Onglets
    tab1, tab2, tab3 = st.tabs(["📅 Ce mois", "➕ Ajouter", "📊 Analyse"])

    with tab1:
        render_onglet_mois()

    with tab2:
        render_onglet_ajouter()

    with tab3:
        render_onglet_analyse()


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
    "render_stats_dashboard",
    "render_depense_card",
    "render_formulaire",
    "render_graphique_evolution",
    "render_comparaison_mois",
    "render_onglet_mois",
    "render_onglet_ajouter",
    "render_onglet_analyse",
]
