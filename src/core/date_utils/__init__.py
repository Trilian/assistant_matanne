"""
Utilitaires de date centralisés.

Ce module consolide toutes les fonctions de manipulation de dates/semaines.

Usage:
    from src.core.date_utils import obtenir_debut_semaine, formater_date_fr
"""

from .formatage import (
    format_week_label,
    formater_date_fr,
    formater_jour_fr,
    formater_mois_fr,
    formater_temps,
)
from .helpers import (
    est_aujourd_hui,
    est_weekend,
    get_weekday_index,
    get_weekday_name,
    get_weekday_names,
)
from .periodes import (
    ajouter_jours_ouvres,
    obtenir_bornes_mois,
    obtenir_trimestre,
    plage_dates,
)
from .semaines import (
    obtenir_bornes_semaine,
    obtenir_debut_semaine,
    obtenir_fin_semaine,
    obtenir_jours_semaine,
    obtenir_semaine_precedente,
    obtenir_semaine_suivante,
    semaines_entre,
)

__all__ = [
    # Semaines
    "obtenir_debut_semaine",
    "obtenir_fin_semaine",
    "obtenir_bornes_semaine",
    "obtenir_jours_semaine",
    "obtenir_semaine_precedente",
    "obtenir_semaine_suivante",
    "semaines_entre",
    # Périodes
    "obtenir_bornes_mois",
    "obtenir_trimestre",
    "plage_dates",
    "ajouter_jours_ouvres",
    # Helpers
    "est_weekend",
    "est_aujourd_hui",
    "get_weekday_names",
    "get_weekday_name",
    "get_weekday_index",
    # Formatage
    "formater_date_fr",
    "formater_jour_fr",
    "formater_mois_fr",
    "format_week_label",
    "formater_temps",
]
