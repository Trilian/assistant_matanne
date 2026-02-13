"""
Formatters - Point d'entrée unifié
"""

# Dates
from .dates import (
    formater_date,
    formater_datetime,
    formater_duree,
    formater_temps,
    temps_ecoule,
)

# Numbers
from .numbers import (
    arrondir_intelligent,
    formater_monnaie,
    formater_nombre,
    formater_plage,
    formater_pourcentage,
    formater_prix,
    formater_quantite,
    formater_quantite_unite,
    formater_taille_fichier,
)

# Text
from .text import (
    capitaliser_mots,
    capitaliser_premiere,
    extraire_nombre,
    generer_slug,
    nettoyer_texte,
    tronquer,
)

# Units
from .units import (
    formater_poids,
    formater_temperature,
    formater_volume,
)

__all__ = [
    # Dates
    "formater_date",
    "formater_datetime",
    "temps_ecoule",
    "formater_temps",
    "formater_duree",
    # Numbers
    "formater_quantite",
    "formater_quantite_unite",
    "formater_prix",
    "formater_monnaie",
    "formater_pourcentage",
    "formater_nombre",
    "formater_taille_fichier",
    "formater_plage",
    "arrondir_intelligent",
    # Text
    "tronquer",
    "nettoyer_texte",
    "generer_slug",
    "extraire_nombre",
    "capitaliser_premiere",
    "capitaliser_mots",
    # Units
    "formater_poids",
    "formater_volume",
    "formater_temperature",
]
