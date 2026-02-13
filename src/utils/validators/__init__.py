"""
Validators - Point d'entrée unifié
"""

# Common
from .common import (
    borner,
    valider_champs_requis,
    valider_choix,
    valider_email,
    valider_longueur_texte,
    valider_plage,
    valider_telephone,
    valider_url,
)

# Dates
from .dates import (
    est_dans_x_jours,
    est_date_future,
    est_date_passee,
    jours_jusqua,
    valider_date_peremption,
    valider_plage_dates,
)

# Food
from .food import (
    valider_allergie,
    valider_article_courses,
    valider_article_inventaire,
    valider_ingredient,
    valider_quantite,
    valider_recette,
    valider_repas,
)

__all__ = [
    # Common
    "valider_email",
    "valider_telephone",
    "valider_url",
    "borner",
    "valider_plage",
    "valider_longueur_texte",
    "valider_champs_requis",
    "valider_choix",
    # Dates
    "valider_plage_dates",
    "est_date_future",
    "est_date_passee",
    "valider_date_peremption",
    "jours_jusqua",
    "est_dans_x_jours",
    # Food
    "valider_quantite",
    "valider_allergie",
    "valider_recette",
    "valider_ingredient",
    "valider_article_inventaire",
    "valider_article_courses",
    "valider_repas",
]
