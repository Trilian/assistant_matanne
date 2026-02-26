"""
Package planning services.

Services liés au planning et calendrier:
- ServiceConflits: Détection de conflits d'horaires
- ServiceRappels: Rappels intelligents adaptatifs
- ServiceSuggestions: Suggestions IA créneaux libres et optimisation
"""

from .conflits import (
    Conflit,
    NiveauConflit,
    RapportConflits,
    ServiceConflits,
    TypeConflit,
    obtenir_service_conflits,
)
from .rappels import (
    PrioriteRappel,
    Rappel,
    ServiceRappels,
    obtenir_service_rappels,
)
from .suggestions import (
    CreneauLibre,
    ServiceSuggestions,
    SuggestionPlanning,
    obtenir_service_suggestions,
)

__all__ = [
    "Conflit",
    "NiveauConflit",
    "RapportConflits",
    "ServiceConflits",
    "TypeConflit",
    "obtenir_service_conflits",
    "PrioriteRappel",
    "Rappel",
    "ServiceRappels",
    "obtenir_service_rappels",
    "CreneauLibre",
    "ServiceSuggestions",
    "SuggestionPlanning",
    "obtenir_service_suggestions",
]
