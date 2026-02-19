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
    Notification,
    # Alias rétrocompatibilité
    NotificationService,
    ServiceNotificationsInventaire,
    obtenir_service_notifications,
    obtenir_service_notifications_inventaire,
)
from src.services.core.notifications.notif_ntfy import (
    NotificationPushConfig,
    NotificationPushScheduler,
    # Alias rétrocompatibilité
    NotificationPushService,
    PlanificateurNtfy,
    ResultatEnvoiPush,
    ServiceNtfy,
    get_notification_push_scheduler,
    get_notification_push_service,
    obtenir_planificateur_ntfy,
    obtenir_service_ntfy,
)
from src.services.core.notifications.notif_web import (
    NotificationPreferences,
    PushNotification,
    # Alias rétrocompatibilité
    PushNotificationService,
    PushSubscription,
    ServiceWebPush,
    get_push_notification_service,
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
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════
from src.services.core.notifications.ui import (
    afficher_demande_permission_push,
    afficher_preferences_notification,
    render_notification_preferences,
    # Alias rétrocompatibilité
    render_push_permission_request,
)

# ═══════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════
from src.services.core.notifications.utils import (
    # Alias rétrocompatibilité anglais
    NotificationType,
    build_push_payload,
    build_subscription_info,
    can_send_during_quiet_hours,
    check_notification_type_enabled,
    construire_info_abonnement,
    construire_payload_push,
    create_activity_reminder_notification,
    create_expiration_notification,
    create_meal_reminder_notification,
    create_milestone_reminder_notification,
    create_shopping_shared_notification,
    create_stock_notification,
    creer_notification_liste_partagee,
    creer_notification_peremption,
    creer_notification_rappel_activite,
    creer_notification_rappel_jalon,
    creer_notification_rappel_repas,
    creer_notification_stock,
    doit_envoyer_notification,
    doit_reinitialiser_compteur,
    est_heures_silencieuses,
    generate_count_key,
    generer_cle_compteur,
    get_notification_type_mapping,
    is_quiet_hours,
    # Français
    obtenir_mapping_types_notification,
    parse_count_key,
    parser_cle_compteur,
    peut_envoyer_pendant_silence,
    should_reset_counter,
    should_send_notification,
    validate_preferences,
    validate_subscription,
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
    # === UI (français) ===
    "afficher_demande_permission_push",
    "afficher_preferences_notification",
    # === CONSTANTES ===
    "NTFY_BASE_URL",
    "DEFAULT_TOPIC",
    "PRIORITY_MAPPING",
    "VAPID_PUBLIC_KEY",
    "VAPID_PRIVATE_KEY",
    "VAPID_EMAIL",
    # === ALIAS RÉTROCOMPATIBILITÉ (anglais) ===
    # Types
    "NotificationType",
    "Notification",
    "NotificationPushConfig",
    "ResultatEnvoiPush",
    "PushSubscription",
    "PushNotification",
    "NotificationPreferences",
    # Services
    "NotificationService",
    "obtenir_service_notifications",
    "NotificationPushService",
    "NotificationPushScheduler",
    "get_notification_push_service",
    "get_notification_push_scheduler",
    "PushNotificationService",
    "get_push_notification_service",
    # Utilitaires
    "get_notification_type_mapping",
    "check_notification_type_enabled",
    "is_quiet_hours",
    "can_send_during_quiet_hours",
    "should_send_notification",
    "build_push_payload",
    "build_subscription_info",
    "create_stock_notification",
    "create_expiration_notification",
    "create_meal_reminder_notification",
    "create_shopping_shared_notification",
    "create_activity_reminder_notification",
    "create_milestone_reminder_notification",
    "generate_count_key",
    "parse_count_key",
    "should_reset_counter",
    "validate_subscription",
    "validate_preferences",
    # UI
    "render_push_permission_request",
    "render_notification_preferences",
]
