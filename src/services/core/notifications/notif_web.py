"""
Backward compatibility — imports from split modules.

.. deprecated::
    Importer directement depuis les modules spécifiques :
    - notif_web_core.py: ServiceWebPush, obtenir_service_webpush
    - notif_web_persistence.py: NotificationPersistenceMixin
    - notif_web_templates.py: NotificationTemplatesMixin
    Ou depuis le package: src.services.core.notifications

Ce fichier ne contient que des ré-exports et sera fusionné dans
le __init__.py du package à terme.
"""

from src.services.core.notifications.notif_web_core import (  # noqa: F401
    ServiceWebPush,
    get_push_notification_service,
    obtenir_service_webpush,
)
from src.services.core.notifications.notif_web_persistence import (  # noqa: F401
    NotificationPersistenceMixin,
)
from src.services.core.notifications.notif_web_templates import (  # noqa: F401
    NotificationTemplatesMixin,
)

__all__ = [
    "ServiceWebPush",
    "obtenir_service_webpush",
    "get_push_notification_service",
    "NotificationPersistenceMixin",
    "NotificationTemplatesMixin",
]
