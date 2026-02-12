"""
Module partage pour les constantes et utilitaires communs.

Ce module centralise:
- Les constantes utilisees par plusieurs modules (JOURS_SEMAINE, TYPES_REPAS)
- Les fonctions utilitaires de date/semaine
- Les patterns de validation de base
"""

from src.modules.shared.constantes import (
    JOURS_SEMAINE,
    JOURS_SEMAINE_COURT,
    JOURS_SEMAINE_LOWER,
    TYPES_REPAS,
    MOIS_FRANCAIS,
    MOIS_FRANCAIS_COURT,
)
from src.modules.shared.date_utils import (
    obtenir_debut_semaine,
    obtenir_fin_semaine,
    obtenir_jours_semaine,
    obtenir_semaine_precedente,
    obtenir_semaine_suivante,
    formater_date_fr,
    formater_jour_fr,
)

__all__ = [
    # Constantes
    "JOURS_SEMAINE",
    "JOURS_SEMAINE_COURT",
    "JOURS_SEMAINE_LOWER",
    "TYPES_REPAS",
    "MOIS_FRANCAIS",
    "MOIS_FRANCAIS_COURT",
    # Fonctions date
    "obtenir_debut_semaine",
    "obtenir_fin_semaine",
    "obtenir_jours_semaine",
    "obtenir_semaine_precedente",
    "obtenir_semaine_suivante",
    "formater_date_fr",
    "formater_jour_fr",
]
