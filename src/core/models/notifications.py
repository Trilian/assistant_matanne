"""
Modèles SQLAlchemy pour les notifications push et les webhooks.

Contient :
- AbonnementPush : Abonnements notifications push
- PreferenceNotification : Préférences de notification par utilisateur
- WebhookAbonnement : Webhooks sortants pour notifications externes
"""

from datetime import datetime, time
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, utc_now
from .mixins import CreeLeMixin, TimestampMixin

# ═══════════════════════════════════════════════════════════
# TABLE ABONNEMENTS PUSH
# ═══════════════════════════════════════════════════════════


class AbonnementPush(CreeLeMixin, Base):
    """Abonnement push notification.

    Table SQL: push_subscriptions
    Utilisé par: src/services/push_notifications.py

    Attributes:
        endpoint: URL de l'endpoint push
        p256dh_key: Clé p256dh pour le chiffrement
        auth_key: Clé d'authentification
        device_info: Informations sur l'appareil
    """

    __tablename__ = "abonnements_push"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    endpoint: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    p256dh_key: Mapped[str] = mapped_column(Text, nullable=False)
    auth_key: Mapped[str] = mapped_column(Text, nullable=False)
    device_info: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    # Supabase user
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)

    # Timestamps (last_used reste manuel — nom non-standard)
    last_used: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    def __repr__(self) -> str:
        return f"<AbonnementPush(id={self.id}, user_id={self.user_id})>"


# ═══════════════════════════════════════════════════════════
# TABLE PRÉFÉRENCES NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


class PreferenceNotification(TimestampMixin, Base):
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

    __tablename__ = "preferences_notifications"

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

    def __repr__(self) -> str:
        return f"<PreferenceNotification(id={self.id}, user_id={self.user_id})>"


# ═══════════════════════════════════════════════════════════
# TABLE WEBHOOKS SORTANTS
# ═══════════════════════════════════════════════════════════


class WebhookAbonnement(TimestampMixin, Base):
    """Abonnement webhook pour notifications externes.

    Permet d'envoyer des notifications HTTP POST vers des URLs externes
    quand des événements métier se produisent (recette créée, stock modifié, etc.).

    Table SQL: webhooks_abonnements

    Attributes:
        url: URL de destination du webhook (POST)
        evenements: Patterns d'événements à écouter (ex: ["recette.*", "courses.generees"])
        secret: Clé HMAC-SHA256 pour signer les payloads
        actif: Webhook actif ou désactivé
        description: Description libre
        derniere_livraison: Date de la dernière livraison réussie
        nb_echecs_consecutifs: Compteur d'échecs consécutifs (auto-désactivation à 5)
    """

    __tablename__ = "webhooks_abonnements"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    evenements: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    secret: Mapped[str] = mapped_column(String(128), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    derniere_livraison: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    nb_echecs_consecutifs: Mapped[int] = mapped_column(Integer, default=0)

    # Propriétaire du webhook
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)

    def __repr__(self) -> str:
        return f"<WebhookAbonnement(id={self.id}, url={self.url}, actif={self.actif})>"
