"""
ParisCrudService - Façade composée de mixins pour les paris sportifs.

Refactorisé en 3 mixins (Phase 4 Audit, item 18 — split >500 LOC):
- paris_queries.py (lecture, ~300 LOC)
- paris_mutations.py (écriture, ~140 LOC)
- paris_sync.py (synchronisation API, ~200 LOC)

L'API publique reste identique — seule la structure interne change.

Utilisation:
    service = get_paris_crud_service()
    equipes = service.charger_equipes("Ligue 1")
    service.enregistrer_pari(match_id=1, prediction="1", cote=1.8)
"""

import logging

from src.core.models import PariSportif
from src.services.core.base import BaseService
from src.services.core.registry import service_factory

from .paris_mutations import ParisMutationMixin
from .paris_queries import ParisQueryMixin
from .paris_sync import ParisSyncMixin

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE — FAÇADE COMPOSÉE
# ═══════════════════════════════════════════════════════════


class ParisCrudService(
    ParisQueryMixin, ParisMutationMixin, ParisSyncMixin, BaseService[PariSportif]
):
    """Service CRUD pour les paris sportifs, équipes et matchs.

    Façade composée des 3 mixins:
    - ParisQueryMixin: charger_equipes, charger_matchs_*, charger_paris_*, fallbacks
    - ParisMutationMixin: enregistrer_pari, ajouter_equipe/match, supprimer, résultats
    - ParisSyncMixin: sync_equipes, sync_matchs, refresh_scores

    Hérite de BaseService[PariSportif] pour le CRUD générique.
    """

    def __init__(self):
        super().__init__(model=PariSportif, cache_ttl=60)


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("paris_crud", tags={"jeux", "crud", "paris"})
def get_paris_crud_service() -> ParisCrudService:
    """Factory singleton pour ParisCrudService."""
    return ParisCrudService()


def obtenir_service_paris_crud() -> ParisCrudService:
    """Alias français pour get_paris_crud_service."""
    return get_paris_crud_service()
