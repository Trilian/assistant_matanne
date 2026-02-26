"""
Service Jardin - Gestion intelligente du jardin avec IA.

Facade mince combinant les mixins spécialisés:
- JardinIAMixin: Conseils IA, diagnostic plantes, alertes météo
- JardinCrudMixin: CRUD plantes, zones, stats, logs
- JardinGamificationMixin: Badges, streaks, autonomie alimentaire

Chaque mixin est dans son propre fichier < 500 LOC.
Le fichier principal (facade) reste léger (~120 LOC).
"""

import logging

from src.core.ai import ClientIA, obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.event_bus_mixin import EventBusMixin
from src.services.core.registry import service_factory
from src.services.core.service_health import ServiceHealthCheck, ServiceHealthMixin, StatutService
from src.services.core.service_metrics import ServiceMetricsMixin

from .jardin_crud_mixin import JardinCrudMixin
from .jardin_gamification_mixin import BADGES_JARDIN, JardinGamificationMixin  # noqa: F401
from .jardin_ia_mixin import JardinIAMixin

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE JARDIN (FACADE)
# ═══════════════════════════════════════════════════════════


class JardinService(
    JardinIAMixin,
    JardinCrudMixin,
    JardinGamificationMixin,
    ServiceHealthMixin,
    ServiceMetricsMixin,
    EventBusMixin,
    BaseAIService,
):
    """Service IA pour la gestion intelligente du jardin.

    Facade combinant les mixins spécialisés:
    - JardinIAMixin: Conseils saisonniers, diagnostic, arrosage IA, alertes météo
    - JardinCrudMixin: CRUD plantes, zones, stats, logs
    - JardinGamificationMixin: Badges, streaks, autonomie alimentaire
    - JardinTachesMixin: Génération automatique des tâches (via gamification)
    - JardinCatalogueMixin: Catalogue de plantes (via gamification)

    Hérite aussi de:
    - ServiceHealthMixin: Health checks granulaires
    - ServiceMetricsMixin: Métriques Prometheus
    - EventBusMixin: Émission automatique d'événements

    Example:
        >>> service = get_jardin_service()
        >>> conseils = await service.generer_conseils_saison("printemps")
        >>> taches = service.generer_taches(mes_plantes, meteo)
        >>> stats = service.calculer_stats(plantes, recoltes)
        >>> badges = service.obtenir_badges(stats)
    """

    _event_source = "jardin"

    def __init__(self, client: ClientIA | None = None):
        """Initialise le service jardin.

        Args:
            client: Client IA optionnel (créé automatiquement si None)
        """
        if client is None:
            client = obtenir_client_ia()
        super().__init__(
            client=client,
            cache_prefix="jardin",
            default_ttl=3600,
            service_name="jardin",
        )
        # Sprint 6: Initialiser health checks et métriques
        self._register_health_check()
        self._init_metrics()

    def _health_check_custom(self) -> ServiceHealthCheck:
        """Vérifications de santé spécifiques au jardin."""
        try:
            plantes_count = 0
            try:
                plantes = self.obtenir_plantes()
                plantes_count = len(plantes) if plantes else 0
            except Exception:
                pass

            return ServiceHealthCheck(
                service="jardin",
                status=StatutService.HEALTHY,
                message=f"{plantes_count} plantes dans le jardin",
                details={"plantes_count": plantes_count},
            )
        except Exception as e:
            return ServiceHealthCheck(
                service="jardin",
                status=StatutService.DEGRADED,
                message=str(e),
            )


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def obtenir_service_jardin(client: ClientIA | None = None) -> JardinService:
    """Factory pour obtenir le service jardin (convention française).

    Args:
        client: Client IA optionnel

    Returns:
        Instance de JardinService
    """
    return JardinService(client=client)


@service_factory("jardin", tags={"maison", "crud", "jardin"})
def get_jardin_service(client: ClientIA | None = None) -> JardinService:
    """Factory pour obtenir le service jardin (alias anglais)."""
    return obtenir_service_jardin(client)
