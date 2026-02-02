"""
Package Famille - Hub de vie familiale (refonte 2026-02)

Nouveaux modules:
- hub_famille.py: Dashboard avec cards cliquables (Jules, Weekend, Anne, Mathieu, Achats)
- jules_nouveau.py: Activités adaptées âge + shopping Jules + conseils IA
- suivi_perso.py: Suivi Anne/Mathieu avec Garmin + alimentation
- weekend.py: Planning sorties weekend + suggestions IA
- achats_famille.py: Wishlist famille par catégorie

Modules conservés:
- activites.py: Planning activités générales
- routines.py: Routines quotidiennes
"""

from . import hub_famille, jules, suivi_perso, weekend, achats_famille
from . import activites, routines

__all__ = [
    "hub_famille", "jules", "suivi_perso", "weekend", "achats_famille",
    "activites", "routines",
]

