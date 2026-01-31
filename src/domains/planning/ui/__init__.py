"""
Module Planning - Centre de Coordination Familiale

Agrège TOUS les événements familiaux en une vision unifiée:
- 📅 Calendrier: Tous les événements intégrés
- [CHART] Vue Semaine: Analyse charge et répartition
- 🎯 Vue d'Ensemble: Actions prioritaires et suggestions

Utilise PlanningAIService pour:
✅ Agrégation optimisée avec cache intelligent
✅ Calcul charge familiale jour par jour
✅ Détection alertes intelligentes
✅ Génération IA de semaines équilibrées
"""

from . import calendrier, vue_semaine, vue_ensemble

__all__ = ["calendrier", "vue_semaine", "vue_ensemble"]

# Enregistrement automatique pour OptimizedRouter
SUBMODULES = {
    "📅 Calendrier Familial": calendrier,
    "[CHART] Vue Semaine": vue_semaine,
    "🎯 Vue d'Ensemble": vue_ensemble,
}


def app():
    """Point d'entrée module planning - Affiche la vue d'ensemble par défaut"""
    # Import ici pour éviter de charger Streamlit inutilement
    import streamlit as st

    # Menu de sélection
    st.sidebar.markdown("### 📅 Planning")

    view = st.sidebar.radio(
        "Sélectionner une vue",
        list(SUBMODULES.keys()),
        key="planning_view_selection",
    )

    # Charger la vue sélectionnée
    submodule = SUBMODULES[view]
    submodule.app()

