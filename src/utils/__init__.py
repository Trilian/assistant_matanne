"""
Utils - Point d'entrée unifié optimisé
Organisation claire : formatters/ validators/ helpers/ media/
"""

# Constants
from .constants import *

# Formatters
from .formatters import (
    arrondir_intelligent,
    capitaliser_mots,
    # Text
    capitaliser_premiere,
    extraire_nombre,
    # Dates
    formater_date,
    formater_datetime,
    formater_duree,
    formater_monnaie,
    formater_nombre,
    formater_plage,
    # Units
    formater_poids,
    formater_pourcentage,
    formater_prix,
    # Numbers
    formater_quantite,
    formater_quantite_unite,
    formater_taille_fichier,
    formater_temperature,
    formater_temps,
    formater_volume,
    generer_slug,
    nettoyer_texte,
    temps_ecoule,
    tronquer,
)

# Helpers
from .helpers import (
    ajouter_jours_ouvres,
    aplatir,
    calculer_ecart_type,
    calculer_etendue,
    calculer_mediane,
    calculer_mode,
    # Stats
    calculer_moyenne,
    calculer_percentile,
    calculer_variance,
    camel_vers_snake,
    compter_par,
    # Food (métier) - 3 fonctions pures
    convertir_unite,
    dedupliquer,
    est_aujourd_hui,
    est_weekend,
    extraire,
    extraire_ingredient,
    fusionner_dicts,
    # Strings
    generer_id,
    grouper_par,
    masquer_sensible,
    moyenne_mobile,
    multiplier_portion,
    normaliser_espaces,
    obtenir_bornes_mois,
    # Dates
    obtenir_bornes_semaine,
    obtenir_debut_semaine,
    obtenir_fin_semaine,
    # Data
    obtenir_securise,
    obtenir_trimestre,
    omettre,
    partitionner,
    plage_dates,
    pluraliser,
    retirer_accents,
    semaines_entre,
    snake_vers_camel,
    trier_donnees,
)

# Media
from .media import ImageCache, ImageConfig, ImageOptimizer, get_cache_stats, optimize_uploaded_image

# Validators
from .validators import (
    borner,
    est_dans_x_jours,
    est_date_future,
    est_date_passee,
    jours_jusqua,
    valider_allergie,
    valider_article_courses,
    valider_article_inventaire,
    valider_champs_requis,
    valider_choix,
    valider_date_peremption,
    # Common
    valider_email,
    valider_ingredient,
    valider_longueur_texte,
    valider_plage,
    # Dates
    valider_plage_dates,
    # Food
    valider_quantite,
    valider_recette,
    valider_repas,
    valider_telephone,
    valider_url,
)

__all__ = [
    # Formatters - Text
    "tronquer",
    "nettoyer_texte",
    "generer_slug",
    "extraire_nombre",
    "capitaliser_premiere",
    "capitaliser_mots",
    # Formatters - Dates
    "formater_date",
    "formater_datetime",
    "temps_ecoule",
    "formater_temps",
    "formater_duree",
    # Formatters - Numbers
    "formater_quantite",
    "formater_quantite_unite",
    "formater_prix",
    "formater_monnaie",
    "formater_pourcentage",
    "formater_nombre",
    "formater_taille_fichier",
    "formater_plage",
    "arrondir_intelligent",
    # Formatters - Units
    "formater_poids",
    "formater_volume",
    "formater_temperature",
    # Validators - Common
    "valider_email",
    "valider_telephone",
    "valider_url",
    "borner",
    "valider_plage",
    "valider_longueur_texte",
    "valider_champs_requis",
    "valider_choix",
    # Validators - Dates
    "valider_plage_dates",
    "est_date_future",
    "est_date_passee",
    "valider_date_peremption",
    "jours_jusqua",
    "est_dans_x_jours",
    # Validators - Food
    "valider_quantite",
    "valider_allergie",
    "valider_recette",
    "valider_ingredient",
    "valider_article_inventaire",
    "valider_article_courses",
    "valider_repas",
    # Helpers - Data
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
    # Helpers - Dates
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
    # Helpers - Strings
    "generer_id",
    "normaliser_espaces",
    "retirer_accents",
    "camel_vers_snake",
    "snake_vers_camel",
    "pluraliser",
    "masquer_sensible",
    # Helpers - Stats
    "calculer_moyenne",
    "calculer_mediane",
    "calculer_variance",
    "calculer_ecart_type",
    "calculer_percentile",
    "calculer_mode",
    "calculer_etendue",
    "moyenne_mobile",
    # Helpers - Food (3 fonctions pures)
    "convertir_unite",
    "multiplier_portion",
    "extraire_ingredient",
    # Media
    "ImageOptimizer",
    "ImageCache",
    "ImageConfig",
    "optimize_uploaded_image",
    "get_cache_stats",
]
