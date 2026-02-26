"""
Logique metier du module Courses - Separee de l'UI
Ce module contient toute la logique pure, testable sans Streamlit.

Hub de re-exports: les implementations sont dans utils_operations.py et utils_formatage.py
"""

# Re-export depuis utils_operations (constantes, filtrage, tri, groupement, validation)
# Re-export depuis utils_formatage (statistiques, formatage, suggestions, historique)
from .utils_formatage import (
    analyser_historique,
    calculer_statistiques,
    calculer_statistiques_par_rayon,
    deduper_suggestions,
    formater_article_label,
    formater_liste_impression,
    generer_modele_depuis_historique,
    generer_suggestions_depuis_recettes,
    generer_suggestions_depuis_stock_bas,
)
from .utils_operations import (
    PRIORITY_EMOJIS,
    PRIORITY_ORDER,
    RAYONS_DEFAULT,
    filtrer_articles,
    filtrer_par_priorite,
    filtrer_par_rayon,
    filtrer_par_recherche,
    get_current_user_id,
    grouper_par_priorite,
    grouper_par_rayon,
    trier_par_nom,
    trier_par_priorite,
    trier_par_rayon,
    valider_article,
    valider_nouvel_article,
)

__all__ = [
    # Constantes
    "PRIORITY_EMOJIS",
    "PRIORITY_ORDER",
    "RAYONS_DEFAULT",
    # Filtrage
    "filtrer_articles",
    "filtrer_par_priorite",
    "filtrer_par_rayon",
    "filtrer_par_recherche",
    # Tri
    "trier_par_nom",
    "trier_par_priorite",
    "trier_par_rayon",
    # Groupement
    "grouper_par_priorite",
    "grouper_par_rayon",
    # Validation
    "valider_article",
    "valider_nouvel_article",
    # Statistiques
    "calculer_statistiques",
    "calculer_statistiques_par_rayon",
    # Formatage
    "formater_article_label",
    "formater_liste_impression",
    # Suggestions
    "generer_suggestions_depuis_stock_bas",
    "generer_suggestions_depuis_recettes",
    "deduper_suggestions",
    # Historique
    "analyser_historique",
    "generer_modele_depuis_historique",
    # Utilitaires
    "get_current_user_id",
]
