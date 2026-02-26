"""
Service Projets - Gestion intelligente des projets maison avec estimation IA.

Facade mince combinant les mixins spécialisés:
- ProjetsIAMixin: Estimation IA, suggestions, budget, ROI
- ProjetsCrudMixin: CRUD projets/tâches, stats, événements

Chaque mixin est dans son propre fichier < 500 LOC.
Le fichier principal (facade) reste léger (~120 LOC).
"""

import logging
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from src.core.ai import ClientIA, obtenir_client_ia
from src.core.models import Projet
from src.services.core.base import BaseAIService
from src.services.core.event_bus_mixin import EventBusMixin
from src.services.core.registry import service_factory
from src.services.core.service_health import ServiceHealthCheck, ServiceHealthMixin, StatutService
from src.services.core.service_metrics import ServiceMetricsMixin

from .projets_crud_mixin import ProjetsCrudMixin
from .projets_ia_mixin import ProjetsIAMixin
from .schemas import (  # noqa: F401
    MaterielProjet,
    ProjetEstimation,
    TacheProjetCreate,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

CATEGORIES_PROJET = [
    "travaux",
    "renovation",
    "amenagement",
    "reparation",
    "decoration",
    "jardin",
    "exterieur",
]

PRIORITES = ["haute", "moyenne", "basse"]

MAGASINS_BRICOLAGE = [
    "Leroy Merlin",
    "Castorama",
    "Brico Dépôt",
    "Mr Bricolage",
    "Bricomarché",
]


# ═══════════════════════════════════════════════════════════
# SERVICE PROJETS (FACADE)
# ═══════════════════════════════════════════════════════════


class ProjetsService(
    ProjetsIAMixin,
    ProjetsCrudMixin,
    ServiceHealthMixin,
    ServiceMetricsMixin,
    EventBusMixin,
    BaseAIService,
):
    """Service IA pour la gestion intelligente des projets maison.

    Facade combinant les mixins spécialisés:
    - ProjetsIAMixin: Estimation complète, budget, alternatives, ROI
    - ProjetsCrudMixin: CRUD projets/tâches, stats, événements

    Hérite aussi de:
    - ServiceHealthMixin: Health checks granulaires
    - ServiceMetricsMixin: Métriques Prometheus
    - EventBusMixin: Émission automatique d'événements

    Example:
        >>> service = get_projets_service()
        >>> estimation = await service.estimer_projet("Repeindre chambre", "15m², 2 couches")
        >>> print(estimation.materiels_necessaires)
    """

    _event_source = "projets"

    def __init__(self, client: ClientIA | None = None):
        """Initialise le service projets.

        Args:
            client: Client IA optionnel
        """
        if client is None:
            client = obtenir_client_ia()
        super().__init__(
            client=client,
            cache_prefix="projets",
            default_ttl=3600,
            service_name="projets",
        )
        self._register_health_check()
        self._init_metrics()

    def _health_check_custom(self) -> ServiceHealthCheck:
        """Vérifications de santé spécifiques aux projets."""
        try:
            projets_count = 0
            projets_urgents = 0
            try:
                projets = self.obtenir_projets()
                projets_count = len(projets) if projets else 0
                urgents = self.obtenir_projets_urgents()
                projets_urgents = len(urgents) if urgents else 0
            except Exception:
                pass

            return ServiceHealthCheck(
                service="projets",
                status=StatutService.HEALTHY,
                message=f"{projets_count} projets ({projets_urgents} urgents)",
                details={
                    "projets_count": projets_count,
                    "projets_urgents": projets_urgents,
                },
            )
        except Exception as e:
            return ServiceHealthCheck(
                service="projets",
                status=StatutService.DEGRADED,
                message=str(e),
            )


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def obtenir_service_projets(client: ClientIA | None = None) -> ProjetsService:
    """Factory pour obtenir le service projets (convention française).

    Args:
        client: Client IA optionnel

    Returns:
        Instance de ProjetsService
    """
    return ProjetsService(client=client)


@service_factory("projets", tags={"maison", "crud", "projets"})
def get_projets_service(client: ClientIA | None = None) -> ProjetsService:
    """Factory pour obtenir le service projets (alias anglais)."""
    return obtenir_service_projets(client)
