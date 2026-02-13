"""
Modèles SQLAlchemy pour les notifications push.

Contient :
- PushSubscription : Abonnements notifications push
- NotificationPreference : Préférences de notification par utilisateur
"""

from datetime import datetime, time
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

# ═══════════════════════════════════════════════════════════
# TABLE ABONNEMENTS PUSH
# ═══════════════════════════════════════════════════════════


class PushSubscription(Base):
    """Abonnement push notification.

    Table SQL: push_subscriptions
    Utilisé par: src/services/push_notifications.py

    Attributes:
        endpoint: URL de l'endpoint push
        p256dh_key: Clé p256dh pour le chiffrement
        auth_key: Clé d'authentification
        device_info: Informations sur l'appareil
    """

    __tablename__ = "push_subscriptions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    endpoint: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    p256dh_key: Mapped[str] = mapped_column(Text, nullable=False)
    auth_key: Mapped[str] = mapped_column(Text, nullable=False)
    device_info: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    # Supabase user
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_used: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<PushSubscription(id={self.id}, user_id={self.user_id})>"


# ═══════════════════════════════════════════════════════════
# TABLE PRÉFÉRENCES NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


class NotificationPreference(Base):
    """Préférences de notification par utilisateur.

    Table SQL: notification_preferences

    Attributes:
        courses_rappel: Rappel courses
        repas_suggestion: Suggestions de repas
        stock_alerte: Alertes de stock
        meteo_alerte: Alertes météo
        budget_alerte: Alertes budget
        quiet_hours_start: Début des heures silencieuses
        quiet_hours_end: Fin des heures silencieuses
    """

    __tablename__ = "notification_preferences"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # Préférences
    courses_rappel: Mapped[bool] = mapped_column(Boolean, default=True)
    repas_suggestion: Mapped[bool] = mapped_column(Boolean, default=True)
    stock_alerte: Mapped[bool] = mapped_column(Boolean, default=True)
    meteo_alerte: Mapped[bool] = mapped_column(Boolean, default=True)
    budget_alerte: Mapped[bool] = mapped_column(Boolean, default=True)

    # Heures silencieuses
    quiet_hours_start: Mapped[time | None] = mapped_column(Time, default=time(22, 0))
    quiet_hours_end: Mapped[time | None] = mapped_column(Time, default=time(7, 0))

    # Supabase user (unique)
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), unique=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<NotificationPreference(id={self.id}, user_id={self.user_id})>"
