"""
Module Planning - Centre de Coordination Familiale

AgrÃ¨ge TOUS les Ã©vÃ©nements familiaux en une vision unifiÃ©e:
- ðŸ“… Calendrier: Tous les Ã©vÃ©nements intÃ©grÃ©s
- ðŸ“Š Vue Semaine: Analyse charge et rÃ©partition
- ðŸŽ¯ Vue d'Ensemble: Actions prioritaires et suggestions

Utilise PlanningAIService pour:
âœ… AgrÃ©gation optimisÃ©e avec cache intelligent
âœ… Calcul charge familiale jour par jour
âœ… DÃ©tection alertes intelligentes
âœ… GÃ©nÃ©ration IA de semaines Ã©quilibrÃ©es
"""

from . import calendrier, vue_semaine, vue_ensemble

__all__ = ["calendrier", "vue_semaine", "vue_ensemble"]

# Enregistrement automatique pour OptimizedRouter
SUBMODULES = {
    "ðŸ“… Calendrier Familial": calendrier,
    "ðŸ“Š Vue Semaine": vue_semaine,
    "ðŸŽ¯ Vue d'Ensemble": vue_ensemble,
}


def app():
    """Point d'entrÃ©e module planning - Affiche la vue d'ensemble par dÃ©faut"""
    # Import ici pour Ã©viter de charger Streamlit inutilement
    import streamlit as st

    # Menu de sÃ©lection
    st.sidebar.markdown("### ðŸ“… Planning")

    view = st.sidebar.radio(
        "SÃ©lectionner une vue",
        list(SUBMODULES.keys()),
        key="planning_view_selection",
    )

    # Charger la vue sÃ©lectionnÃ©e
    submodule = SUBMODULES[view]
    submodule.app()

