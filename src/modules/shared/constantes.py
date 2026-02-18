"""
Constantes partagees entre tous les modules.

DEPRECATED: Ce module re-exporte depuis src.core.constants.
Utilisez directement: from src.core.constants import ...
"""

# Re-export depuis core/constants pour rétrocompatibilité
from src.core.constants import (
    JOURS_SEMAINE,
    JOURS_SEMAINE_COURT,
    JOURS_SEMAINE_LOWER,
    MOIS_FRANCAIS,
    MOIS_FRANCAIS_COURT,
    TYPES_PROTEINES,
    TYPES_REPAS_AFFICHAGE,
)
from src.core.constants import (
    TYPES_REPAS_KEYS as TYPES_REPAS,
)

__all__ = [
    "JOURS_SEMAINE",
    "JOURS_SEMAINE_COURT",
    "JOURS_SEMAINE_LOWER",
    "MOIS_FRANCAIS",
    "MOIS_FRANCAIS_COURT",
    "TYPES_REPAS",
    "TYPES_REPAS_AFFICHAGE",
    "TYPES_PROTEINES",
]
