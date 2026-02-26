"""Package core - Services fondamentaux (auth, backup, notifications, events, registry).

Imports paresseux pour éviter les imports circulaires.
Importez directement depuis les sous-packages:

    from src.services.core.base import BaseService, BaseAIService
    from src.services.core.base import CRUDProtocol, AIServiceProtocol  # Protocols PEP 544
    from src.services.core.base import Result, Success, Failure, success, failure  # Result[T]
    from src.services.core.events import obtenir_bus, EvenementDomaine  # Event Bus
    from src.services.core.registry import registre, obtenir_registre  # Service Registry
    from src.services.core.backup import obtenir_service_backup
    from src.services.core.notifications import obtenir_service_notifications
    from src.services.core.utilisateur import get_auth_service

    # Health checks & Metrics (Sprint 6)
    from src.services.core.service_health import (
        ServiceHealthMixin, obtenir_sante_services, initialiser_health_services
    )
    from src.services.core.service_metrics import (
        ServiceMetricsMixin, obtenir_metriques_services, exporter_prometheus_services
    )
    from src.services.core.event_bus_mixin import EventBusMixin, emettre_apres_crud
"""

__all__ = [
    "base",
    "backup",
    "events",
    "notifications",
    "registry",
    "utilisateur",
    "event_bus_mixin",
    "service_health",
    "service_metrics",
]


def __getattr__(name: str):
    """Lazy import pour éviter les imports circulaires."""
    # Base services
    if name == "BaseService":
        from src.services.core.base import BaseService

        return BaseService
    if name == "BaseAIService":
        from src.services.core.base import BaseAIService

        return BaseAIService

    # CQS (Command/Query Separation)
    if name in (
        "QueryService",
        "CommandService",
        "CRUDService",
        "QueryProtocol",
        "CommandProtocol",
    ):
        from src.services.core import cqs as cqs_mod

        return getattr(cqs_mod, name)

    if name == "IOService":
        from src.services.core.base import IOService

        return IOService

    # Result[T, E]
    if name in ("Result", "Success", "Failure", "success", "failure", "ErrorCode", "ErrorInfo"):
        from src.services.core.base import result as result_mod

        return getattr(result_mod, name)

    # Event Bus
    if name == "obtenir_bus":
        from src.services.core.events import obtenir_bus

        return obtenir_bus
    if name == "BusEvenements":
        from src.services.core.events import BusEvenements

        return BusEvenements

    # Registry
    if name == "registre":
        from src.services.core.registry import registre

        return registre
    if name == "obtenir_registre":
        from src.services.core.registry import obtenir_registre

        return obtenir_registre
    if name == "service_factory":
        from src.services.core.registry import service_factory

        return service_factory

    # Backup
    if name == "ServiceBackup":
        from src.services.core.backup import ServiceBackup

        return ServiceBackup
    if name == "obtenir_service_backup":
        from src.services.core.backup import obtenir_service_backup

        return obtenir_service_backup

    # Notifications
    if name == "obtenir_service_notifications":
        from src.services.core.notifications import obtenir_service_notifications

        return obtenir_service_notifications

    # Auth
    if name == "AuthService":
        from src.services.core.utilisateur import AuthService

        return AuthService
    if name == "get_auth_service":
        from src.services.core.utilisateur import get_auth_service

        return get_auth_service

    # Event Bus Mixin (Sprint 6)
    if name == "EventBusMixin":
        from src.services.core.event_bus_mixin import EventBusMixin

        return EventBusMixin
    if name == "emettre_apres_crud":
        from src.services.core.event_bus_mixin import emettre_apres_crud

        return emettre_apres_crud
    if name == "avec_evenement":
        from src.services.core.event_bus_mixin import avec_evenement

        return avec_evenement

    # Service Health (Sprint 6)
    if name == "ServiceHealthMixin":
        from src.services.core.service_health import ServiceHealthMixin

        return ServiceHealthMixin
    if name == "obtenir_sante_services":
        from src.services.core.service_health import obtenir_sante_services

        return obtenir_sante_services
    if name == "initialiser_health_services":
        from src.services.core.service_health import initialiser_health_services

        return initialiser_health_services

    # Service Metrics (Sprint 6)
    if name == "ServiceMetricsMixin":
        from src.services.core.service_metrics import ServiceMetricsMixin

        return ServiceMetricsMixin
    if name == "obtenir_metriques_services":
        from src.services.core.service_metrics import obtenir_metriques_services

        return obtenir_metriques_services
    if name == "exporter_prometheus_services":
        from src.services.core.service_metrics import exporter_prometheus_services

        return exporter_prometheus_services

    raise AttributeError(f"module 'src.services.core' has no attribute '{name}'")
