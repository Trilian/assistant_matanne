"""
Logique metier du module Batch Cooking - Separee de l'UI

Hub de re-exports: les implementations sont dans batch_cooking_temps.py,
batch_cooking_etapes.py et batch_cooking_portions.py
"""

# Re-export depuis batch_cooking_temps (constantes, temps, validation)
# Re-export depuis batch_cooking_etapes (optimisation, conflits)
from .batch_cooking_etapes import (
    detecter_conflits_robots,
    optimiser_ordre_etapes,
)

# Re-export depuis batch_cooking_portions (Jules, statistiques)
from .batch_cooking_portions import (
    calculer_historique_batch,
    calculer_statistiques_session,
    filtrer_etapes_bruyantes,
    generer_planning_jules,
    identifier_moments_jules,
)
from .batch_cooking_temps import (
    JOURS_EMOJI,
    LOCALISATIONS,
    ROBOTS_INFO,
    calculer_duree_totale_optimisee,
    estimer_heure_fin,
    formater_duree,
    valider_preparation,
    valider_session_batch,
)

__all__ = [
    # Constantes
    "JOURS_EMOJI",
    "LOCALISATIONS",
    "ROBOTS_INFO",
    # Temps
    "calculer_duree_totale_optimisee",
    "estimer_heure_fin",
    "formater_duree",
    # Validation
    "valider_preparation",
    "valider_session_batch",
    # Etapes
    "detecter_conflits_robots",
    "optimiser_ordre_etapes",
    # Jules & Statistiques
    "calculer_historique_batch",
    "calculer_statistiques_session",
    "filtrer_etapes_bruyantes",
    "generer_planning_jules",
    "identifier_moments_jules",
]
