"""
Migration 009 - Intégration services avec base de données

Révision ID: 009
Down revision: 008
Date: 2026-01-28

Cette migration documente les changements apportés aux services
pour utiliser les modèles SQLAlchemy (nouveaux.py) au lieu de Pydantic local:

Services migrés:
- weather.py: AlerteMeteo, ConfigMeteo (sauvegarder/lister alertes)
- backup.py: Backup (historique des sauvegardes)
- calendar_sync.py: CalendrierExterne, EvenementCalendrier
- push_notifications.py: PushSubscription, NotificationPreference

Les tables correspondantes ont été créées via SUPABASE_COMPLET_V3.sql:
- alertes_meteo
- config_meteo
- backups
- calendriers_externes
- evenements_calendrier
- push_subscriptions
- notification_preferences

Aucune modification de schéma nécessaire - tables déjà créées.
"""

# Revision identifiers, used by Alembic
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    """
    Les tables existent déjà via SUPABASE_COMPLET_V3.sql.
    Cette migration documente l'intégration des services.
    """
    pass


def downgrade():
    """
    Pas de rollback nécessaire - les services continuent à fonctionner
    avec les modèles Pydantic locaux si la DB n'est pas disponible.
    """
    pass
