"""
Mode Tablette - Module complet pour interfaces tactiles.

Fournit:
- Configuration et gestion du mode tablette
- CSS adapté aux écrans tactiles
- Composants UI optimisés tactiles
- Mode cuisine (recettes step-by-step)
"""

# Configuration et état
from .config import ModeTablette, definir_mode_tablette, obtenir_mode_tablette

# Mode cuisine
from .kitchen import afficher_selecteur_mode, afficher_vue_recette_cuisine

# Styles CSS
from .styles import CSS_MODE_CUISINE, CSS_TABLETTE, appliquer_mode_tablette, fermer_mode_tablette

# Timer cuisine
from .timer import TimerCuisine

# Widgets tactiles
from .widgets import (
    bouton_tablette,
    grille_selection_tablette,
    liste_cases_tablette,
    saisie_nombre_tablette,
)

__all__ = [
    # Config
    "ModeTablette",
    "obtenir_mode_tablette",
    "definir_mode_tablette",
    # Styles
    "CSS_TABLETTE",
    "CSS_MODE_CUISINE",
    "appliquer_mode_tablette",
    "fermer_mode_tablette",
    # Widgets
    "bouton_tablette",
    "grille_selection_tablette",
    "saisie_nombre_tablette",
    "liste_cases_tablette",
    # Kitchen
    "afficher_vue_recette_cuisine",
    "afficher_selecteur_mode",
    # Timer
    "TimerCuisine",
]
