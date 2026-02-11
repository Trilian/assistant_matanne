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

from src.services.notifications.types import (
    # Enums
    TypeAlerte,
    TypeNotification,
    # Modèles inventaire
    NotificationInventaire,
    # Modèles ntfy
    ConfigurationNtfy,
    NotificationNtfy,
    ResultatEnvoiNtfy,
    # Modèles Web Push
    AbonnementPush,
    NotificationPush,
    PreferencesNotification,
    # Constantes
    NTFY_BASE_URL,
    DEFAULT_TOPIC,
    PRIORITY_MAPPING,
    VAPID_PUBLIC_KEY,
    VAPID_PRIVATE_KEY,
    VAPID_EMAIL,
)

# ═══════════════════════════════════════════════════════════
# SERVICES
# ═══════════════════════════════════════════════════════════

from src.services.notifications.inventaire import (
    ServiceNotificationsInventaire,
    obtenir_service_notifications_inventaire,
    # Alias rétrocompatibilité
    NotificationService,
    obtenir_service_notifications,
    Notification,
)

from src.services.notifications.notif_ntfy import (
    ServiceNtfy,
    PlanificateurNtfy,
    obtenir_service_ntfy,
    obtenir_planificateur_ntfy,
    # Alias rétrocompatibilité
    NotificationPushService,
    NotificationPushScheduler,
    NotificationPushConfig,
    ResultatEnvoiPush,
    get_notification_push_service,
    get_notification_push_scheduler,
)

from src.services.notifications.notif_web import (
    ServiceWebPush,
    obtenir_service_webpush,
    # Alias rétrocompatibilité
    PushNotificationService,
    get_push_notification_service,
    PushSubscription,
    PushNotification,
    NotificationPreferences,
)

# ═══════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════

from src.services.notifications.utils import (
    # Français
    obtenir_mapping_types_notification,
    verifier_type_notification_active,
    est_heures_silencieuses,
    peut_envoyer_pendant_silence,
    doit_envoyer_notification,
    construire_payload_push,
    construire_info_abonnement,
    creer_notification_stock,
    creer_notification_peremption,
    creer_notification_rappel_repas,
    creer_notification_liste_partagee,
    creer_notification_rappel_activite,
    creer_notification_rappel_jalon,
    generer_cle_compteur,
    parser_cle_compteur,
    doit_reinitialiser_compteur,
    valider_abonnement,
    valider_preferences,
    # Alias rétrocompatibilité anglais
    NotificationType,
    get_notification_type_mapping,
    check_notification_type_enabled,
    is_quiet_hours,
    can_send_during_quiet_hours,
    should_send_notification,
    build_push_payload,
    build_subscription_info,
    create_stock_notification,
    create_expiration_notification,
    create_meal_reminder_notification,
    create_shopping_shared_notification,
    create_activity_reminder_notification,
    create_milestone_reminder_notification,
    generate_count_key,
    parse_count_key,
    should_reset_counter,
    validate_subscription,
    validate_preferences,
)

# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════

from src.services.notifications.ui import (
    afficher_demande_permission_push,
    afficher_preferences_notification,
    # Alias rétrocompatibilité
    render_push_permission_request,
    render_notification_preferences,
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
