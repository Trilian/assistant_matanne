"""
Helpers - Point d'entrée unifié
"""

# Data
from .data import (
    count_by,
    deduplicate,
    flatten,
    group_by,
    merge_dicts,
    omit,
    partition,
    pick,
    safe_get,
    trier_donnees,
    # Alias français
    obtenir_securise,
    grouper_par,
    compter_par,
    dedupliquer,
    deduplicater,
    aplatir,
    fusionner_listes,
    partitionner,
    fusionner_dicts,
    extraire,
    omettre,
)

# Dates
from .dates import (
    add_business_days,
    date_range,
    get_month_bounds,
    get_quarter,
    get_week_bounds,
    is_weekend,
    weeks_between,
    est_aujourd_hui,
    # Alias français
    obtenir_debut_semaine,
    obtenir_fin_semaine,
    obtenir_bornes_semaine,
    plage_dates,
    obtenir_bornes_mois,
    ajouter_jours_ouvres,
    semaines_entre,
    obtenir_trimestre,
)

# Food (métier cuisine)
from .food import (
    convertir_unite,
    multiplier_portion,
    extraire_ingredient,
)

# Stats
from .stats import (
    calculate_average,
    calculate_median,
    calculate_mode,
    calculate_percentile,
    calculate_range,
    calculate_std_dev,
    calculate_variance,
    moving_average,
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
    "safe_get",
    "group_by",
    "count_by",
    "deduplicate",
    "flatten",
    "partition",
    "merge_dicts",
    "pick",
    "omit",
    # Dates
    "get_week_bounds",
    "date_range",
    "get_month_bounds",
    "add_business_days",
    "weeks_between",
    "is_weekend",
    "get_quarter",
    # Strings
    "generer_id",
    "normaliser_espaces",
    "retirer_accents",
    "camel_vers_snake",
    "snake_vers_camel",
    "pluraliser",
    "masquer_sensible",
    # Stats
    "calculate_average",
    "calculate_median",
    "calculate_variance",
    "calculate_std_dev",
    "calculate_percentile",
    "calculate_mode",
    "calculate_range",
    "moving_average",
    # Food
    "convertir_unite",
    "multiplier_portion",
    "extraire_ingredient",
    # Alias français - Data
    "obtenir_securise",
    "grouper_par",
    "compter_par",
    "dedupliquer",
    "deduplicater",
    "aplatir",
    "fusionner_listes",
    "partitionner",
    "fusionner_dicts",
    "extraire",
    "omettre",
    "trier_donnees",
    # Alias français - Dates
    "obtenir_debut_semaine",
    "obtenir_fin_semaine",
    "obtenir_bornes_semaine",
    "plage_dates",
    "obtenir_bornes_mois",
    "ajouter_jours_ouvres",
    "semaines_entre",
    "est_aujourd_hui",
    "obtenir_trimestre",
]
