"""
UI Feedback - Point d'entrée
Feedback temps réel pour l'utilisateur
"""

# Spinners
# Progress
from .progress import EtatChargement, SuiviProgression

# Result → Streamlit
from .results import (
    afficher_resultat,
    afficher_resultat_toast,
    result_avec_spinner,
    result_ou_none,
    result_ou_vide,
)
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
    # Result → Streamlit
    "afficher_resultat",
    "afficher_resultat_toast",
    "result_ou_vide",
    "result_ou_none",
    "result_avec_spinner",
]
