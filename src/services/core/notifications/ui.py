"""
DEPRECATED: Ce fichier a été déplacé vers src/ui/views/notifications.py

Ce module est conservé pour la rétrocompatibilité temporaire.
Veuillez mettre à jour vos imports:

    # Ancien import (deprecated)
    from src.services.core.notifications.ui import afficher_demande_permission_push

    # Nouvel import
    from src.ui.views.notifications import afficher_demande_permission_push
"""

import warnings

# Réexporter depuis le nouvel emplacement
from src.ui.views.notifications import (
    afficher_demande_permission_push,
    afficher_preferences_notification,
)

# Alias de compatibilité anglais
render_notification_preferences = afficher_preferences_notification
render_push_permission_request = afficher_demande_permission_push

# Émettre un avertissement à l'import
warnings.warn(
    "src.services.notifications.ui est déprécié. Utilisez src.ui.views.notifications à la place.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "afficher_demande_permission_push",
    "afficher_preferences_notification",
    # Alias anglais
    "render_notification_preferences",
    "render_push_permission_request",
]
