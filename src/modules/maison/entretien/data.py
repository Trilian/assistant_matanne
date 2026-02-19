"""
Entretien - Chargement des données.

⚠️ charger_catalogue_entretien est maintenant un PROXY vers le service.
Le catalogue est chargé depuis le service centralisé.
"""

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CHARGEMENT DONNÉES - PROXY VERS SERVICE
# ═══════════════════════════════════════════════════════════


@lru_cache(maxsize=1)
def _get_service():
    """Retourne une instance singleton du service entretien."""
    from src.services.maison import get_entretien_service

    return get_entretien_service()


def charger_catalogue_entretien() -> dict:
    """
    Charge le catalogue des tâches d'entretien.

    Proxy vers EntretienService.charger_catalogue_entretien()
    """
    return _get_service().charger_catalogue_entretien()


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    "charger_catalogue_entretien",
]
