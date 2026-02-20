"""Logique metier du module Inventaire — Re-exports pour compatibilite."""

from .alertes_logic import alertes_critiques_existent, calculer_alertes, compter_alertes
from .constants import CATEGORIES, EMPLACEMENTS, STATUS_CONFIG
from .dataframes import _prepare_alert_dataframe, _prepare_inventory_dataframe
from .filters import (
    filtrer_inventaire,
    filtrer_par_categorie,
    filtrer_par_emplacement,
    filtrer_par_recherche,
    filtrer_par_status,
)
from .formatage import (
    calculer_jours_avant_peremption,
    formater_article_inventaire,
    formater_article_label,
    formater_inventaire_rapport,
    grouper_par_categorie,
    grouper_par_emplacement,
    trier_par_peremption,
    trier_par_urgence,
)
from .stats import (
    calculer_statistiques_inventaire,
    calculer_statistiques_par_categorie,
    calculer_statistiques_par_emplacement,
)
from .status import calculer_status_global, calculer_status_peremption, calculer_status_stock
from .validation import valider_article_inventaire, valider_nouvel_article_inventaire

__all__ = ["_prepare_inventory_dataframe", "_prepare_alert_dataframe"]
