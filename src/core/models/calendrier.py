"""
Modèles SQLAlchemy pour les calendriers externes.

Contient :
- CalendrierExterne : Calendriers synchronisés (Google, Apple, Outlook, iCal)
- EvenementCalendrier : Événements de calendrier synchronisés
"""

from datetime import datetime
from enum import Enum, StrEnum
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, utc_now

# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════


class CalendarProvider(StrEnum):
    """Fournisseurs de calendrier."""

    GOOGLE = "google"
    APPLE = "apple"
    OUTLOOK = "outlook"
    ICAL_URL = "ical_url"


class SyncDirection(StrEnum):
    """Direction de synchronisation calendrier."""

    IMPORT = "import"
    EXPORT = "export"
    BIDIRECTIONAL = "bidirectional"


# ═══════════════════════════════════════════════════════════
# TABLE CALENDRIERS EXTERNES
# ═══════════════════════════════════════════════════════════


class CalendrierExterne(Base):
    """Calendrier externe synchronisé.

    Table SQL: calendriers_externes
    Utilisé par: src/services/calendar_sync.py

    Attributes:
        provider: Fournisseur (google, apple, outlook, ical)
        nom: Nom du calendrier
        url: URL du calendrier (pour iCal)
        credentials: Tokens OAuth chiffrés
        enabled: Si la synchronisation est active
        sync_interval_minutes: Intervalle de synchro en minutes
        last_sync: Dernière synchronisation
        sync_direction: Direction de synchro
    """

    __tablename__ = "calendriers_externes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    provider: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str | None] = mapped_column(Text)
    credentials: Mapped[dict | None] = mapped_column(JSONB)  # Tokens OAuth
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_interval_minutes: Mapped[int] = mapped_column(Integer, default=60)
    last_sync: Mapped[datetime | None] = mapped_column(DateTime)
    sync_direction: Mapped[str] = mapped_column(String(20), default="bidirectional")

    # Supabase user
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )

    # Relations
    evenements: Mapped[list["EvenementCalendrier"]] = relationship(
        back_populates="calendrier_source", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<CalendrierExterne(id={self.id}, provider='{self.provider}', nom='{self.nom}')>"


# ═══════════════════════════════════════════════════════════
# TABLE ÉVÉNEMENTS CALENDRIER
# ═══════════════════════════════════════════════════════════


class EvenementCalendrier(Base):
    """Événement de calendrier synchronisé.

    Table SQL: evenements_calendrier

    Attributes:
        uid: UID iCal unique
        titre: Titre de l'événement
        description: Description
        date_debut: Date/heure de début
        date_fin: Date/heure de fin
        lieu: Lieu
        all_day: Si c'est un événement sur toute la journée
        recurrence_rule: Règle de récurrence RRULE
        rappel_minutes: Rappel avant l'événement
        source_calendrier_id: ID du calendrier source
    """

    __tablename__ = "evenements_calendrier"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    uid: Mapped[str] = mapped_column(String(255), nullable=False)
    titre: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    date_debut: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    date_fin: Mapped[datetime | None] = mapped_column(DateTime)
    lieu: Mapped[str | None] = mapped_column(String(300))
    all_day: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_rule: Mapped[str | None] = mapped_column(Text)  # RRULE iCal
    rappel_minutes: Mapped[int | None] = mapped_column(Integer)

    # Relation calendrier source
    source_calendrier_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("calendriers_externes.id", ondelete="SET NULL")
    )

    # Supabase user
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )

    __table_args__ = (UniqueConstraint("uid", "user_id", name="uq_event_uid_user"),)

    # Relations
    calendrier_source: Mapped[Optional["CalendrierExterne"]] = relationship(
        back_populates="evenements"
    )

    def __repr__(self) -> str:
        return f"<EvenementCalendrier(id={self.id}, titre='{self.titre}', date={self.date_debut})>"
