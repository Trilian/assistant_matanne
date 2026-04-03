"""
Services Innovations — Innovations & IA du planning.

Regroupe les services d'innovation et valeur ajoutée :
- Bilan annuel automatique IA
- Score bien-être familial composite
- Enrichissement contacts IA
- Analyse tendances Loto/Euromillions
- Optimisation parcours magasin IA
- Veille emploi multi-sites
- Mode invité (lien partageable)
"""

from .service import (
    InnovationsService,
    get_innovations_service,
)

__all__ = [
    "InnovationsService",
    "get_innovations_service",
]
