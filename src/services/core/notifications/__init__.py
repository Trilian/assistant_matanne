"""
Package de notifications unifié.

Fusionne les 3 anciens services:
- notifications.py → inventaire.py (notifications locales inventaire)
- notifications_push.py → ntfy.py (notifications via ntfy.sh)
- push_notifications.py → webpush.py (notifications Web Push API)

Tous renommés en français avec alias rétrocompatibilité.
"""

# ═══════════════════════════════════════════════════════════
# TYPES ET ENUMS
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# SERVICES
# ═══════════════════════════════════════════════════════════
from src.services.core.notifications.inventaire import (
    ServiceNotificationsInventaire,
    obtenir_service_notifications_inventaire,
)
from src.services.core.notifications.notif_ntfy import (
    PlanificateurNtfy,
    ServiceNtfy,
    obtenir_planificateur_ntfy,
    obtenir_service_ntfy,
)
from src.services.core.notifications.notif_web import (
    ServiceWebPush,
    obtenir_service_webpush,
)
from src.services.core.notifications.types import (
    DEFAULT_TOPIC,
    # Constantes
    NTFY_BASE_URL,
    PRIORITY_MAPPING,
    VAPID_EMAIL,
    VAPID_PRIVATE_KEY,
    VAPID_PUBLIC_KEY,
    # Modèles Web Push
    AbonnementPush,
    # Modèles ntfy
    ConfigurationNtfy,
    # Modèles inventaire
    NotificationInventaire,
    NotificationNtfy,
    NotificationPush,
    PreferencesNotification,
    ResultatEnvoiNtfy,
    # Enums
    TypeAlerte,
    TypeNotification,
)

# ═══════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════
from src.services.core.notifications.utils import (
    construire_info_abonnement,
    construire_payload_push,
    creer_notification_liste_partagee,
    creer_notification_peremption,
    creer_notification_rappel_activite,
    creer_notification_rappel_jalon,
    creer_notification_rappel_repas,
    creer_notification_stock,
    doit_envoyer_notification,
    doit_reinitialiser_compteur,
    est_heures_silencieuses,
    generer_cle_compteur,
    obtenir_mapping_types_notification,
    parser_cle_compteur,
    peut_envoyer_pendant_silence,
    valider_abonnement,
    valider_preferences,
    verifier_type_notification_active,
)

# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # === TYPES (français) ===
    "TypeAlerte",
    "TypeNotification",
    "NotificationInventaire",
    "ConfigurationNtfy",
    "NotificationNtfy",
    "ResultatEnvoiNtfy",
    "AbonnementPush",
    "NotificationPush",
    "PreferencesNotification",
    # === SERVICES (français) ===
    "ServiceNotificationsInventaire",
    "obtenir_service_notifications_inventaire",
    "ServiceNtfy",
    "PlanificateurNtfy",
    "obtenir_service_ntfy",
    "obtenir_planificateur_ntfy",
    "ServiceWebPush",
    "obtenir_service_webpush",
    # === UTILITAIRES (français) ===
    "obtenir_mapping_types_notification",
    "verifier_type_notification_active",
    "est_heures_silencieuses",
    "peut_envoyer_pendant_silence",
    "doit_envoyer_notification",
    "construire_payload_push",
    "construire_info_abonnement",
    "creer_notification_stock",
    "creer_notification_peremption",
    "creer_notification_rappel_repas",
    "creer_notification_liste_partagee",
    "creer_notification_rappel_activite",
    "creer_notification_rappel_jalon",
    "generer_cle_compteur",
    "parser_cle_compteur",
    "doit_reinitialiser_compteur",
    "valider_abonnement",
    "valider_preferences",
    # === CONSTANTES ===
    "NTFY_BASE_URL",
    "DEFAULT_TOPIC",
    "PRIORITY_MAPPING",
    "VAPID_PUBLIC_KEY",
    "VAPID_PRIVATE_KEY",
    "VAPID_EMAIL",
]
