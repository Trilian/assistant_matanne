"""
Migration 009 - IntÃ©gration services avec base de donnÃ©es

RÃ©vision ID: 009
Down revision: 008
Date: 2026-01-28

Cette migration documente les changements apportÃ©s aux services
pour utiliser les modÃ¨les SQLAlchemy (nouveaux.py) au lieu de Pydantic local:

Services migrÃ©s:
- weather.py: AlerteMeteo, ConfigMeteo (sauvegarder/lister alertes)
- backup.py: Backup (historique des sauvegardes)
- calendar_sync.py: CalendrierExterne, EvenementCalendrier
- push_notifications.py: PushSubscription, NotificationPreference

Les tables correspondantes ont Ã©tÃ© crÃ©Ã©es via SUPABASE_COMPLET_V3.sql:
- alertes_meteo
- config_meteo
- backups
- calendriers_externes
- evenements_calendrier
- push_subscriptions
- notification_preferences

Aucune modification de schÃ©ma nÃ©cessaire - tables dÃ©jÃ  crÃ©Ã©es.
"""

# Revision identifiers, used by Alembic
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    """
    Les tables existent dÃ©jÃ  via SUPABASE_COMPLET_V3.sql.
    Cette migration documente l'intÃ©gration des services.
    """
    pass


def downgrade():
    """
    Pas de rollback nÃ©cessaire - les services continuent Ã  fonctionner
    avec les modÃ¨les Pydantic locaux si la DB n'est pas disponible.
    """
    pass
