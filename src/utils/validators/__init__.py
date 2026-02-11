"""
Validators - Point d'entrée unifié
"""

# Common
from .common import (
    valider_email,
    valider_telephone,
    valider_url,
    borner,
    valider_plage,
    valider_longueur_texte,
    valider_champs_requis,
    valider_choix,
)

# Dates
from .dates import (
    jours_jusqua,
    est_date_future,
    est_date_passee,
    est_dans_x_jours,
    valider_plage_dates,
    valider_date_peremption,
)

# Food
from .food import (
    valider_quantite,
    valider_allergie,
    valider_recette,
    valider_ingredient,
    valider_article_inventaire,
    valider_article_courses,
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
