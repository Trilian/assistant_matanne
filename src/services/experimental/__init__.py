"""
Couche de compatibilité pour les innovations historiques.

Le point d'entrée recommandé passe désormais par les packages métier
(`src.services.cuisine`, `famille`, `maison`, `rapports`, `ia_avancee`).
Ce module reste conservé pour la rétrocompatibilité des imports existants.
"""

from .service import (
    InnovationsService,
    get_innovations_service,
)

__all__ = [
    "InnovationsService",
    "get_innovations_service",
]
