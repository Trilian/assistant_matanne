"""
Module infrastructure - Services techniques transversaux.

Ce module regroupe les services d'infrastructure:
- Notifications (push, email, préférences)
- Rapports (génération PDF, exports)
- Sauvegarde (backup/restore)
- Utilisateur (authentification, historique)
"""

# Ré-export depuis les sous-modules pour compatibilité
from src.services.backup import (
    BackupService,
    ServiceBackup,
    get_backup_service,
    obtenir_service_backup,
)
from src.services.notifications import (
    NotificationService,
    PushNotificationService,
    ServiceNotificationsInventaire,
    ServiceWebPush,
    get_push_notification_service,
    obtenir_service_notifications,
    obtenir_service_webpush,
)
from src.services.rapports import (
    PDFExportService,
    RapportsPDFService,
    ServiceExportPDF,
    ServiceRapportsPDF,
    get_pdf_export_service,
    get_rapports_pdf_service,
    obtenir_service_export_pdf,
    obtenir_service_rapports_pdf,
)
from src.services.utilisateur import (
    ActionHistoryService,
    AuthService,
    UserPreferenceService,
    get_action_history_service,
    get_auth_service,
    get_user_preference_service,
)

__all__ = [
    # Notifications
    "NotificationService",
    "ServiceNotificationsInventaire",
    "obtenir_service_notifications",
    "PushNotificationService",
    "ServiceWebPush",
    "get_push_notification_service",
    "obtenir_service_webpush",
    # Rapports
    "PDFExportService",
    "ServiceExportPDF",
    "get_pdf_export_service",
    "obtenir_service_export_pdf",
    "RapportsPDFService",
    "ServiceRapportsPDF",
    "get_rapports_pdf_service",
    "obtenir_service_rapports_pdf",
    # Backup
    "BackupService",
    "ServiceBackup",
    "get_backup_service",
    "obtenir_service_backup",
    # Utilisateur
    "AuthService",
    "get_auth_service",
    "UserPreferenceService",
    "get_user_preference_service",
    "ActionHistoryService",
    "get_action_history_service",
]
