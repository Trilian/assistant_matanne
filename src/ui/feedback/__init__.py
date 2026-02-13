"""
UI Feedback - Point d'entrée
Feedback temps réel pour l'utilisateur
"""

# Spinners
# Progress
from .progress import EtatChargement, SuiviProgression
from .spinners import chargeur_squelette, indicateur_chargement, spinner_intelligent

# Notifications
from .toasts import (
    GestionnaireNotifications,
    afficher_avertissement,
    afficher_erreur,
    afficher_info,
    afficher_succes,
)

__all__ = [
    # Spinners
    "spinner_intelligent",
    "indicateur_chargement",
    "chargeur_squelette",
    # Progress
    "SuiviProgression",
    "EtatChargement",
    # Notifications
    "GestionnaireNotifications",
    "afficher_succes",
    "afficher_erreur",
    "afficher_avertissement",
    "afficher_info",
]
