"""
Modèles SQLAlchemy pour le jardin et la météo.

Contient :
- AlerteMeteo : Alertes météo pour le jardin
- ConfigMeteo : Configuration météo par utilisateur
"""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import CreatedAtMixin, TimestampFullMixin

# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════


class NiveauAlerte(StrEnum):
    """Niveaux d'alerte météo."""

    INFO = "info"
    ATTENTION = "attention"
    DANGER = "danger"


class TypeAlerteMeteo(StrEnum):
    """Types d'alertes météo."""

    GEL = "gel"
    CANICULE = "canicule"
    PLUIE_FORTE = "pluie_forte"
    VENT_FORT = "vent_fort"
    GRELE = "grele"
    NEIGE = "neige"


# ═══════════════════════════════════════════════════════════
# TABLE ALERTES MÉTÉO
# ═══════════════════════════════════════════════════════════


class AlerteMeteo(CreatedAtMixin, Base):
    """Alerte météo pour le jardin.

    Table SQL: alertes_meteo
    Utilisé par: src/services/weather.py

    Attributes:
        type_alerte: Type d'alerte (gel, canicule, etc.)
        niveau: Niveau (info, attention, danger)
        titre: Titre de l'alerte
        message: Message détaillé
        conseil_jardin: Conseil pour le jardin
        date_debut: Date de début de l'alerte
        date_fin: Date de fin
        temperature: Température associée
        lu: Si l'alerte a été lue
    """

    __tablename__ = "alertes_meteo"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    type_alerte: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    niveau: Mapped[str] = mapped_column(String(20), nullable=False, default="info")
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    conseil_jardin: Mapped[str | None] = mapped_column(Text)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    date_fin: Mapped[date | None] = mapped_column(Date)
    temperature: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    lu: Mapped[bool] = mapped_column(Boolean, default=False)

    # Supabase user
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)

    def __repr__(self) -> str:
        return f"<AlerteMeteo(id={self.id}, type='{self.type_alerte}', niveau='{self.niveau}')>"


# ═══════════════════════════════════════════════════════════
# TABLE CONFIGURATION MÉTÉO
# ═══════════════════════════════════════════════════════════


class ConfigMeteo(TimestampFullMixin, Base):
    """Configuration météo par utilisateur.

    Table SQL: config_meteo

    Attributes:
        latitude: Latitude (par défaut Paris)
        longitude: Longitude (par défaut Paris)
        ville: Nom de la ville
        surface_jardin_m2: Surface du jardin en m²
        notifications_*: Préférences de notifications
    """

    __tablename__ = "config_meteo"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), default=Decimal("48.8566"))
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), default=Decimal("2.3522"))
    ville: Mapped[str] = mapped_column(String(100), default="Paris")
    surface_jardin_m2: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("50"))

    # Préférences notifications
    notifications_gel: Mapped[bool] = mapped_column(Boolean, default=True)
    notifications_canicule: Mapped[bool] = mapped_column(Boolean, default=True)
    notifications_pluie: Mapped[bool] = mapped_column(Boolean, default=True)

    # Supabase user (unique)
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), unique=True)

    def __repr__(self) -> str:
        return f"<ConfigMeteo(id={self.id}, ville='{self.ville}')>"
