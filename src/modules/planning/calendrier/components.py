"""
Module Calendrier Familial Unifié - Composants UI

Hub de ré-export pour compatibilité arrière.
Les composants sont désormais organisés en sous-modules :
- components_jour : affichage d'un jour (calendrier, sortable, cellule)
- components_semaine : vues semaine (grille, liste, stats, actions, impression)
- components_formulaire : navigation, formulaire d'ajout, légende
"""

# --- Composants Jour ---
# --- Navigation, Formulaires, Légende ---
from .components_formulaire import (
    afficher_formulaire_ajout_event,
    afficher_legende,
    afficher_navigation_semaine,
)
from .components_jour import (
    afficher_cellule_jour,
    afficher_jour_calendrier,
    afficher_jour_sortable,
)

# --- Composants Semaine ---
from .components_semaine import (
    afficher_actions_rapides,
    afficher_modal_impression,
    afficher_stats_semaine,
    afficher_vue_semaine_grille,
    afficher_vue_semaine_liste,
)

__all__ = [
    # Jour
    "afficher_jour_calendrier",
    "afficher_jour_sortable",
    "afficher_cellule_jour",
    # Semaine
    "afficher_vue_semaine_grille",
    "afficher_vue_semaine_liste",
    "afficher_stats_semaine",
    "afficher_actions_rapides",
    "afficher_modal_impression",
    # Formulaires & navigation
    "afficher_navigation_semaine",
    "afficher_formulaire_ajout_event",
    "afficher_legende",
]
