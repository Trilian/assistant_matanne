"""
Ancien module logic paris - rétro-compatibilité.
La logique a été migrée vers src.services.jeux.prediction_service.
"""

from src.services.jeux.prediction_service import (
    generer_conseil_pari,
    generer_conseils_avances,
    predire_over_under,
    predire_resultat_match,
)

__all__ = [
    "predire_resultat_match",
    "predire_over_under",
    "generer_conseils_avances",
    "generer_conseil_pari",
]
