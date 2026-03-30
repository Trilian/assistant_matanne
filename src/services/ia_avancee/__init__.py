"""
Services IA Avancée — Phase 6 du planning.

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

__all__ = [
    "IAAvanceeService",
    "get_ia_avancee_service",
]
