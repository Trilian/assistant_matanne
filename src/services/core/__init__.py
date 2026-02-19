"""Package core - Services fondamentaux (auth, backup, notifications).

Imports paresseux pour éviter les imports circulaires.
Importez directement depuis les sous-packages:

    from src.services.core.base import BaseService, BaseAIService
    from src.services.core.backup import obtenir_service_backup
    from src.services.core.notifications import obtenir_service_notifications
    from src.services.core.utilisateur import get_auth_service
"""

__all__ = [
    "base",
    "backup",
    "notifications",
    "utilisateur",
]


def __getattr__(name: str):
    """Lazy import pour éviter les imports circulaires."""
    if name == "BaseService":
        from src.services.core.base import BaseService

        return BaseService
    if name == "BaseAIService":
        from src.services.core.base import BaseAIService

        return BaseAIService
    if name == "IOService":
        from src.services.core.base import IOService

        return IOService
    if name == "ServiceBackup":
        from src.services.core.backup import ServiceBackup

        return ServiceBackup
    if name == "obtenir_service_backup":
        from src.services.core.backup import obtenir_service_backup

        return obtenir_service_backup
    if name == "obtenir_service_notifications":
        from src.services.core.notifications import obtenir_service_notifications

        return obtenir_service_notifications
    if name == "AuthService":
        from src.services.core.utilisateur import AuthService

        return AuthService
    if name == "get_auth_service":
        from src.services.core.utilisateur import get_auth_service

        return get_auth_service
    raise AttributeError(f"module 'src.services.core' has no attribute '{name}'")
