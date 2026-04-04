"""
Services IA Avancée — modules IA avancée.

Regroupe les 14 services IA proactifs et contextuels :
- Suggestions achats (historique consommation)
- Planning adaptatif (météo + énergie + budget)
- Diagnostic plantes photo (Pixtral)
- Prévision dépenses fin de mois
- Idées cadeaux IA (anniversaires)
- Analyse photo multi-usage
- Optimisation routines IA
- Analyse documents OCR
- Estimation travaux photo
- Planning voyage IA
- Recommandations économies énergie
- Prédiction pannes entretien
- Suggestions proactives
- Météo → Planning adapté
"""

from .service import (
    IAAvanceeService,
    get_ia_avancee_service,
)
from src.services.experimental import InnovationsService


def get_innovations_service() -> InnovationsService:
    """Délègue dynamiquement au namespace historique pour préserver la rétrocompatibilité."""
    from src.services.experimental import get_innovations_service as _get_innovations_service

    return _get_innovations_service()

__all__ = [
    "IAAvanceeService",
    "get_ia_avancee_service",
    "InnovationsService",
    "get_innovations_service",
]
