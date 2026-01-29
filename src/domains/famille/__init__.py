"""Domaine Famille - Gestion famille (Jules, santÃ©, activitÃ©s, shopping)."""

# UI
from .ui import jules, sante, activites, bien_etre, shopping, routines, suivi_jules

# Logic
from .logic import (
    jules_logic, sante_logic, activites_logic, bien_etre_logic, 
    shopping_logic, routines_logic, suivi_jules_logic, helpers
)

__all__ = [
    # UI
    "jules", "sante", "activites", "bien_etre", "shopping", "routines", "suivi_jules",
    # Logic
    "jules_logic", "sante_logic", "activites_logic", "bien_etre_logic",
    "shopping_logic", "routines_logic", "suivi_jules_logic", "helpers",
]

