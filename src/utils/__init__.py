"""
Utils - Point d'entrée unifié optimisé
Organisation claire : formatters/ validators/ helpers/ media/
"""

# Constants
from .constants import *

# Formatters
from .formatters import (
    # Text
    capitaliser_premiere,
    capitaliser_mots,
    nettoyer_texte,
    extraire_nombre,
    generer_slug,
    tronquer,
    # Dates
    formater_date,
    formater_datetime,
    formater_duree,
    formater_temps,
    temps_ecoule,
    # Numbers
    formater_quantite,
    formater_quantite_unite,
    formater_prix,
    formater_monnaie,
    formater_pourcentage,
    formater_nombre,
    formater_taille_fichier,
    formater_plage,
    arrondir_intelligent,
    # Units
    formater_poids,
    formater_volume,
    formater_temperature,
)

# Helpers
from .helpers import (
    # Data
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
    # Dates
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
    # Strings
    generer_id,
    normaliser_espaces,
    retirer_accents,
    camel_vers_snake,
    snake_vers_camel,
    pluraliser,
    masquer_sensible,
    # Stats
    calculer_moyenne,
    calculer_mediane,
    calculer_mode,
    calculer_percentile,
    calculer_etendue,
    calculer_ecart_type,
    calculer_variance,
    moyenne_mobile,
    # Food (métier) - 3 fonctions pures
    convertir_unite,
    multiplier_portion,
    extraire_ingredient,
)

# Media
from .media import ImageCache, ImageConfig, ImageOptimizer, get_cache_stats, optimize_uploaded_image

# Validators
from .validators import (
    # Common
    valider_email,
    valider_telephone,
    valider_url,
    borner,
    valider_plage,
    valider_longueur_texte,
    valider_champs_requis,
    valider_choix,
    # Dates
    valider_plage_dates,
    est_date_future,
    est_date_passee,
    valider_date_peremption,
    jours_jusqua,
    est_dans_x_jours,
    # Food
    valider_quantite,
    valider_allergie,
    valider_recette,
    valider_ingredient,
    valider_article_inventaire,
    valider_article_courses,
    valider_repas,
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
