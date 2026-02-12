"""
Ancien module logic paris - prediction seulement.
Les autres fichiers ont ete migres vers src.modules.jeux.paris.
"""

from .prediction import (
    predire_resultat_match,
    predire_over_under,
)

__all__ = [
    "predire_resultat_match",
    "predire_over_under",
]
