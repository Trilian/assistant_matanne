"""
Module DÃepenses Maison - Suivi des factures (gaz, eau, ÃelectricitÃe, etc.)

Focus sur les dÃepenses rÃecurrentes de la maison avec consommation.
Utilise le service Budget unifiÃe (src/services/budget.py).
"""

from .utils import st, CATEGORY_LABELS

# Import des fonctions pour exposer l'API publique
from .crud import (
    get_depenses_mois, get_depenses_annee, get_depense_by_id,
    create_depense, update_depense, delete_depense,
    get_stats_globales, get_historique_categorie
)
from .components import (
    render_stats_dashboard, render_depense_card, render_formulaire,
    render_graphique_evolution, render_comparaison_mois,
    render_onglet_mois, render_onglet_ajouter, render_onglet_analyse
)


def app():
    """Point d'entrÃee module DÃepenses"""
    st.title("ðŸ’° DÃepenses Maison")
    st.caption("Suivez vos dÃepenses: gaz, eau, ÃelectricitÃe, loyer...")
    
    # Mode Ãedition
    if "edit_depense_id" in st.session_state:
        depense = get_depense_by_id(st.session_state["edit_depense_id"])
        if depense:
            st.subheader(f"âœï¸ Modifier: {CATEGORY_LABELS.get(depense.categorie, depense.categorie)}")
            if st.button("âŒ Annuler"):
                del st.session_state["edit_depense_id"]
                st.rerun()
            render_formulaire(depense)
            del st.session_state["edit_depense_id"]
            return
    
    # Dashboard
    render_stats_dashboard()
    
    st.divider()
    
    # Onglets
    tab1, tab2, tab3 = st.tabs(["ðŸ“… Ce mois", "âž• Ajouter", "ðŸ“ˆ Analyse"])
    
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
