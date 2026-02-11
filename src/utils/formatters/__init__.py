"""
Formatters - Point d'entrée unifié
"""

# Dates
from .dates import (
    formater_date,
    formater_datetime,
    temps_ecoule,
    formater_temps,
    formater_duree,
)

# Numbers
from .numbers import (
    formater_quantite,
    formater_quantite_unite,
    formater_prix,
    formater_monnaie,
    formater_pourcentage,
    formater_nombre,
    formater_taille_fichier,
    formater_plage,
    arrondir_intelligent,
)

# Text
from .text import (
    capitaliser_premiere,
    nettoyer_texte,
    extraire_nombre,
    generer_slug,
    tronquer,
    capitaliser_mots,
)

# Units
from .units import (
    formater_poids,
    formater_volume,
    formater_temperature,
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
