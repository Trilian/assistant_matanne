"""Package tabs pour Hub Maison Intégré.

Contient les fonctions de tabs extraites de hub_integre.py:
- plan_maison: Vue interactive des pièces
- jardin: Vue des zones et plantes
- chrono: Chronomètre d'entretien
- temps: Dashboard temps passé
- objets: Objets à remplacer
"""

from .chrono import tab_chrono
from .jardin import tab_jardin
from .objets import tab_objets
from .plan_maison import tab_plan_maison
from .temps import tab_temps

__all__ = [
    "tab_chrono",
    "tab_jardin",
    "tab_objets",
    "tab_plan_maison",
    "tab_temps",
]
