"""
Module de paris sportifs - Analyse et prédiction.

Ce package fournit des outils pour:
- Calculer la forme des équipes
- Prédire les résultats de matchs
- Détecter les value bets
- Analyser les tendances des championnats

Usage:
    from src.domains.jeux.logic.paris import (
        calculer_forme_equipe,
        predire_resultat_match,
        AnalyseurParis,
        generer_analyse_complete
    )
"""

# Constants
from .constants import (
    CHAMPIONNATS,
    AVANTAGE_DOMICILE,
    SEUIL_CONFIANCE_HAUTE,
    SEUIL_CONFIANCE_MOYENNE,
    SEUIL_SERIE_SANS_NUL,
    BONUS_NUL_PAR_MATCH,
    POIDS_FORME,
)

# Forme et historique
from .forme import (
    calculer_forme_equipe,
    calculer_serie_sans_nul,
    calculer_bonus_nul_regression,
    calculer_historique_face_a_face,
)

# Prédiction
from .prediction import (
    predire_resultat_match,
    generer_conseil_pari,
    predire_over_under,
    generer_conseils_avances,
)

# Statistiques
from .stats import (
    calculer_performance_paris,
    analyser_tendances_championnat,
    calculer_regularite_equipe,
)

# Analyseur principal
from .analyseur import (
    AnalyseurParis,
    generer_analyse_complete,
    generer_resume_parieur,
)

__all__ = [
    # Constants
    "CHAMPIONNATS",
    "AVANTAGE_DOMICILE",
    "SEUIL_CONFIANCE_HAUTE",
    "SEUIL_CONFIANCE_MOYENNE",
    "SEUIL_SERIE_SANS_NUL",
    "BONUS_NUL_PAR_MATCH",
    "POIDS_FORME",
    # Forme
    "calculer_forme_equipe",
    "calculer_serie_sans_nul",
    "calculer_bonus_nul_regression",
    "calculer_historique_face_a_face",
    # Prediction
    "predire_resultat_match",
    "generer_conseil_pari",
    "predire_over_under",
    "generer_conseils_avances",
    # Stats
    "calculer_performance_paris",
    "analyser_tendances_championnat",
    "calculer_regularite_equipe",
    # Analyseur
    "AnalyseurParis",
    "generer_analyse_complete",
    "generer_resume_parieur",
]
