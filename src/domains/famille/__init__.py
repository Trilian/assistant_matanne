"""Domaine Famille - Gestion famille (Jules, santé, activités, shopping).

Nouveaux modules (refonte 2026-02):
- hub_famille.py: Dashboard avec cards cliquables
- jules_nouveau.py: Activités adaptées âge + shopping + conseils IA
- suivi_perso.py: Anne & Mathieu, Garmin, alimentation
- weekend.py: Planning weekend + suggestions IA
- achats_famille.py: Wishlist famille par catégorie

Modules conservés:
- activites.py: Planning activités générales
- routines.py: Routines quotidiennes
"""

# UI - Nouveaux modules
from .ui import hub_famille, jules, suivi_perso, weekend, achats_famille
from .ui import activites, routines

# Logic - conservés
from .logic import (
    activites_logic, routines_logic, helpers
)

__all__ = [
    # UI - Nouveau hub
    "hub_famille", "jules", "suivi_perso", "weekend", "achats_famille",
    # UI - Conservés
    "activites", "routines",
    # Logic
    "activites_logic", "routines_logic", "helpers",
]

