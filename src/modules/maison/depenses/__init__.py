"""
Module Dépenses Maison - Suivi des factures (gaz, eau, électricité, etc.)

Focus sur les dépenses récurrentes de la maison avec consommation.
Fonctionnalités avancées:
- Graphiques Plotly interactifs
- Export PDF/CSV
- Prévisions IA

Utilise le service Budget unifié (src/services/budget.py).
"""

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


def app():
    """Point d'entrée module Dépenses"""
    st.title("💰 Dépenses Maison")
    st.caption(
        "Suivez vos dépenses: gaz, eau, électricité, loyer... avec graphiques et prévisions IA!"
    )

    # Mode édition
    if "edit_depense_id" in st.session_state:
        depense = get_depense_by_id(st.session_state["edit_depense_id"])
        if depense:
            st.subheader(f"✏️ Modifier: {CATEGORY_LABELS.get(depense.categorie, depense.categorie)}")
            if st.button("❌ Annuler"):
                del st.session_state["edit_depense_id"]
                st.rerun()
            afficher_formulaire(depense)
            del st.session_state["edit_depense_id"]
            return

    # Dashboard
    afficher_stats_dashboard()

    st.divider()

    # Onglets enrichis
    tab1, tab2, tab3 = st.tabs(["📅 Ce mois", "➕ Ajouter", "📊 Analyse"])

    with tab1:
        afficher_onglet_mois()

    with tab2:
        afficher_onglet_ajouter()

    with tab3:
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
