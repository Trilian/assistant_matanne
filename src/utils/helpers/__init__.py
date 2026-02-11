"""
Helpers - Point d'entrée unifié
"""

# Data
from .data import (
    obtenir_securise,
    grouper_par,
    compter_par,
    dedupliquer,
    aplatir,
    partitionner,
    fusionner_dicts,
    extraire,
    omettre,
    trier_donnees,
)

# Dates
from .dates import (
    obtenir_bornes_semaine,
    plage_dates,
    obtenir_bornes_mois,
    ajouter_jours_ouvres,
    semaines_entre,
    est_weekend,
    obtenir_trimestre,
    est_aujourd_hui,
    obtenir_debut_semaine,
    obtenir_fin_semaine,
)

# Food (métier cuisine)
from .food import (
    convertir_unite,
    multiplier_portion,
    extraire_ingredient,
)

# Stats
from .stats import (
    calculer_moyenne,
    calculer_mediane,
    calculer_mode,
    calculer_percentile,
    calculer_etendue,
    calculer_ecart_type,
    calculer_variance,
    moyenne_mobile,
)

# Strings
from .strings import (
    camel_vers_snake,
    generer_id,
    masquer_sensible,
    normaliser_espaces,
    pluraliser,
    retirer_accents,
    snake_vers_camel,
)

__all__ = [
    # Data
    "obtenir_securise",
    "grouper_par",
    "compter_par",
    "dedupliquer",
    "aplatir",
    "partitionner",
    "fusionner_dicts",
    "extraire",
    "omettre",
    "trier_donnees",
    # Dates
    "obtenir_bornes_semaine",
    "plage_dates",
    "obtenir_bornes_mois",
    "ajouter_jours_ouvres",
    "semaines_entre",
    "est_weekend",
    "obtenir_trimestre",
    "est_aujourd_hui",
    "obtenir_debut_semaine",
    "obtenir_fin_semaine",
    # Strings
    "generer_id",
    "normaliser_espaces",
    "retirer_accents",
    "camel_vers_snake",
    "snake_vers_camel",
    "pluraliser",
    "masquer_sensible",
    # Stats
    "calculer_moyenne",
    "calculer_mediane",
    "calculer_variance",
    "calculer_ecart_type",
    "calculer_percentile",
    "calculer_mode",
    "calculer_etendue",
    "moyenne_mobile",
    # Food
    "convertir_unite",
    "multiplier_portion",
    "extraire_ingredient",
]
