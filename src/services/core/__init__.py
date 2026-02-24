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
"""

__all__ = [
    "base",
    "backup",
    "events",
    "notifications",
    "registry",
    "utilisateur",
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
    if name == "IOService":
        from src.services.core.base import IOService

        return IOService

    # Protocols (PEP 544)
    if name == "CRUDProtocol":
        from src.services.core.base.protocols import CRUDProtocol

        return CRUDProtocol
    if name == "AIServiceProtocol":
        from src.services.core.base.protocols import AIServiceProtocol

        return AIServiceProtocol

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

    raise AttributeError(f"module 'src.services.core' has no attribute '{name}'")
