"""
Module Planning - Centre de Coordination Familiale

Agrège TOUS les événements familiaux en une vision unifiée:
- ðŸ“… Calendrier: Tous les événements intégrés
- [CHART] Vue Semaine: Analyse charge et répartition
- 🎯 Vue d'Ensemble: Actions prioritaires et suggestions

Utilise PlanningAIService pour:
âœ… Agrégation optimisée avec cache intelligent
âœ… Calcul charge familiale jour par jour
âœ… Détection alertes intelligentes
âœ… Génération IA de semaines équilibrées
"""

from . import calendrier, vue_semaine, vue_ensemble

__all__ = ["calendrier", "vue_semaine", "vue_ensemble"]

# Enregistrement automatique pour OptimizedRouter
SUBMODULES = {
    "ðŸ“… Calendrier Familial": calendrier,
    "[CHART] Vue Semaine": vue_semaine,
    "🎯 Vue d'Ensemble": vue_ensemble,
}


def app():
    """Point d'entrée module planning - Affiche la vue d'ensemble par défaut"""
    # Import ici pour éviter de charger Streamlit inutilement
    import streamlit as st

    # Menu de sélection
    st.sidebar.markdown("### ðŸ“… Planning")

    view = st.sidebar.radio(
        "Sélectionner une vue",
        list(SUBMODULES.keys()),
        key="planning_view_selection",
    )

    # Charger la vue sélectionnée
    submodule = SUBMODULES[view]
    submodule.app()

